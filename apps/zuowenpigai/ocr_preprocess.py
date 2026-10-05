# -*- coding: utf-8 -*-
"""
ocr_preprocess.py —— OCR 前图像预处理（2026-07-12 决策）
================================================================
目的：提升 GLM-OCR 对手写作文照片的识别率 → 提高逐字引文匹配存活率
     → 增加错字病句检出量（严格闸门不变，从源头补量）。

只做两件温和的事（刻意克制，防止过度处理吃掉笔画）：
  ① 倾斜纠正（deskew）：用方格稿纸的横线估计倾角，仅在 0.4°–8° 之间纠正
     （太小不值得重采样，太大多半是估错了，宁可不动）
  ② 光照均衡 + 温和对比增强：LAB 空间 L 通道做背景除法（压阴影）+ CLAHE
     （clipLimit=2.0，保守值；不做二值化——二值化会毁笔画）

★ 关键边界：预处理结果【只喂给 OCR 接口】。
  session_state 里存的仍是学生原始照片——manuscript_locator 的墨水检测、
  原图批改视图、PDF 左图右评全部继续用原图。倾角纠正不会影响定位：
  定位是"OCR 文字 ↔ 原图字槽"的对齐，文字内容相同即可。

失败即放行：任何一步异常都返回原始 bytes，OCR 流程绝不因预处理中断。

算力：单张 4000px 照片全流程 <0.3 秒（纯 OpenCV CPU 操作），
Streamlit Community Cloud 无压力。零新依赖（opencv-python-headless 已在
requirements.txt）。
"""
import io

import cv2
import numpy as np

# 倾角纠正的启用区间（度）
DESKEW_MIN_DEG = 0.4
DESKEW_MAX_DEG = 8.0
# CLAHE 保守参数
CLAHE_CLIP = 2.0
CLAHE_GRID = (8, 8)
# 重新编码质量（喂 OCR 用，92 已足够无损感）
JPEG_QUALITY = 92


def _estimate_skew_deg(gray):
    """用方格稿纸的横线估计倾角。返回度数（逆时针为正），估不出返回 0。

    方法：边缘 → 概率霍夫直线 → 只取接近水平（±15°内）的长线段 →
    取角度中位数。稿纸横线又多又长，是最稳的倾角来源；
    没有稿纸线（白纸作文）时长横线不足，自然返回 0 = 不纠。
    """
    h, w = gray.shape[:2]
    # 缩到宽 1200 提速，角度不受缩放影响
    scale = 1200.0 / w if w > 1200 else 1.0
    small = cv2.resize(gray, None, fx=scale, fy=scale) if scale < 1.0 else gray
    edges = cv2.Canny(small, 50, 150)
    min_len = int(small.shape[1] * 0.35)          # 至少 35% 页宽才算"横线"
    lines = cv2.HoughLinesP(edges, 1, np.pi / 360, threshold=120,
                            minLineLength=min_len, maxLineGap=8)
    if lines is None:
        return 0.0
    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        ang = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if abs(ang) <= 15.0:                      # 只信接近水平的线
            angles.append(ang)
    if len(angles) < 3:                           # 样本太少，宁可不动
        return 0.0
    return float(np.median(angles))


def _deskew(img_bgr):
    """按估计倾角旋转纠正。角度在启用区间外则原样返回。"""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    ang = _estimate_skew_deg(gray)
    if not (DESKEW_MIN_DEG <= abs(ang) <= DESKEW_MAX_DEG):
        return img_bgr
    h, w = img_bgr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), ang, 1.0)
    # 白色填充：稿纸背景是白的，旋转空角不产生黑边干扰 OCR
    return cv2.warpAffine(img_bgr, M, (w, h),
                          flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT,
                          borderValue=(255, 255, 255))


def _enhance(img_bgr):
    """光照均衡（背景除法压阴影）+ 温和 CLAHE。只动 L 通道，保住笔迹颜色。"""
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)
    # ① 背景除法：大核模糊估计光照背景，逐像素归一 → 阴影、侧光被拉平
    bg = cv2.GaussianBlur(L, (0, 0), sigmaX=max(img_bgr.shape[1] // 30, 15))
    bg = np.clip(bg, 1, 255)
    L = np.clip(L.astype(np.float32) / bg.astype(np.float32) * 220.0,
                0, 255).astype(np.uint8)
    # ② 温和 CLAHE
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=CLAHE_GRID)
    L = clahe.apply(L)
    return cv2.cvtColor(cv2.merge([L, A, B]), cv2.COLOR_LAB2BGR)


def preprocess_for_ocr(img_bytes):
    """入口：原始照片 bytes → 预处理后 JPEG bytes（只供 OCR 使用）。

    返回 (bytes, applied)：applied 为本次实际做了的步骤列表（诊断用）。
    任何异常 → 返回 (原始 bytes, [])，绝不阻断 OCR。
    """
    try:
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return img_bytes, []
        applied = []

        out = _deskew(img)
        if out is not img:
            applied.append("deskew")
        img = out

        img = _enhance(img)
        applied.append("clahe")

        ok, buf = cv2.imencode(".jpg", img,
                               [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ok:
            return img_bytes, []
        return buf.tobytes(), applied
    except Exception:
        return img_bytes, []

