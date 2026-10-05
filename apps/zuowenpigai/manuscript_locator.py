# -*- coding: utf-8 -*-
"""
manuscript_locator.py v2 —— 方格稿纸字级定位引擎（2026-07-08）
================================================================
v2 关键升级：**全局对齐**。不再要求 OCR 按物理行输出——
现有按段落输出的 OCR 全文直接可用（部署零前置条件）。

原理：整篇识别文本作为一条字符流，与"全页字槽流"（逐行墨水槽
按阅读顺序串联）做一次全局动态规划对齐；标点允许附着前一槽，
换行由墨水位置自己决定，无须任何行信息。

用法：
    loc = ManuscriptLocator.from_text(img_bgr, ocr_full_text)
    if loc.confidence >= 0.75:
        rects = loc.locate("浮現")   # -> [(x%,y%,w%,h%), ...]

失败即降级：置信度低 / quote 找不到 → locate() 返回 []，
调用方回退到识别稿视图，绝不硬猜坐标。
"""
import cv2
import numpy as np

PUNCT = set('，。；：？！、""''（）《》—…·,.;:?!()"\' ')


# ---------------- 墨水掩膜 ----------------
def ink_mask(img_bgr, hue=(90, 140), s_min=60, v=(40, 230)):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    m = (H >= hue[0]) & (H <= hue[1]) & (S >= s_min) & (V >= v[0]) & (V <= v[1])
    return m.astype(np.uint8) * 255


def ink_mask_auto(img_bgr):
    """蓝笔优先；黑笔/铅笔走 v2.1 深色管线（2026-07-08）：
    自适应阈值抗光照不均 → 剔除老师红笔 → 形态学去网格长线
    → 连通域去阴影/装订孔大块。"""
    m = ink_mask(img_bgr)
    if m.sum() / 255 > 15000:
        return m
    Himg, Wimg = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    H, S = hsv[:, :, 0], hsv[:, :, 1]
    red = ((H <= 12) | (H >= 168)) & (S >= 70)
    ad = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 35, 12)
    ad[red] = 0
    hk = cv2.getStructuringElement(cv2.MORPH_RECT, (Wimg // 10, 1))
    vk = cv2.getStructuringElement(cv2.MORPH_RECT, (1, Himg // 10))
    ink = cv2.subtract(cv2.subtract(ad, cv2.morphologyEx(ad, cv2.MORPH_OPEN, hk)),
                       cv2.morphologyEx(ad, cv2.MORPH_OPEN, vk))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(ink, 8)
    clean = np.zeros_like(ink)
    for i in range(1, n):
        _x, _y, w, h, area = stats[i]
        if area > 4000 or w > Wimg * 0.5 or h > Himg * 0.3:
            continue          # 阴影/装订孔/残余长线
        clean[lab == i] = 255
    return clean


# ---------------- 行与字槽 ----------------
def detect_rows(mask, min_density=8, min_height=16):
    proj = mask.sum(axis=1) / 255
    rows, in_row, start = [], False, 0
    for y, v in enumerate(proj):
        if v > min_density and not in_row:
            start, in_row = y, True
        elif v <= min_density and in_row:
            if y - start > min_height:
                rows.append((start, y))
            in_row = False
    if in_row:
        rows.append((start, len(proj)))
    return rows


def estimate_pitch(mask, rows):
    spans = []
    for y0, y1 in rows:
        band = mask[max(0, y0 - 4):y1 + 4, :]
        cols = np.where(band.sum(axis=0) > 0)[0]
        if len(cols):
            spans.append(cols[-1] - cols[0])
    if not spans:
        return 36.0
    return float(np.percentile(spans, 90)) / 19.0


def row_slots(mask, y0, y1, pitch, gap=5, min_w=6):
    band = mask[max(0, y0 - 4):y1 + 4, :]
    proj = band.sum(axis=0) / 255
    boxes, in_c, sx, gapc = [], False, 0, 0
    for x, v in enumerate(proj):
        if v > 0 and not in_c:
            sx, in_c, gapc = x, True, 0
        elif in_c:
            if v > 0:
                gapc = 0
            else:
                gapc += 1
                if gapc >= gap:
                    if x - gapc - sx + 1 >= min_w:
                        boxes.append((sx, x - gapc + 1))
                    in_c = False
    if in_c and len(proj) - sx >= min_w:
        boxes.append((sx, len(proj)))
    slots = []
    for x1, x2 in boxes:
        n = max(1, round((x2 - x1) / pitch))
        w = (x2 - x1) / n
        for k in range(n):
            slots.append((x1 + k * w, x1 + (k + 1) * w))
    return slots


# ---------------- 全局对齐 ----------------
def align_global(chars, slots):
    """chars: 全文字符列表（含标点，已去空白换行）
    slots: [(row_idx, x1, x2), ...] 全页字槽流（阅读顺序）
    返回 pos: 每个字符对应 (row_idx, x1, x2) 或 None；conf 置信度。"""
    n, m = len(chars), len(slots)
    if n == 0 or m == 0:
        return None, 0.0
    INF = 1e18
    prev = np.full(m + 1, INF)
    prev[0] = 0.0
    prev_bt = [None] * (m + 1)
    bts = [prev_bt]
    for j in range(1, m + 1):            # 开头允许跳槽（噪点）
        prev[j] = prev[j - 1] + 1.3
        prev_bt[j] = 'skip'
    for i in range(1, n + 1):
        cur = np.full(m + 1, INF)
        cur_bt = [None] * (m + 1)
        c = chars[i - 1]
        is_p = c in PUNCT
        for j in range(m + 1):
            best, op = INF, None
            if j >= 1 and prev[j - 1] < best:            # 字占一槽
                best, op = prev[j - 1], 'take'
            if prev[j] + (0.6 if is_p else 1.5) < best:  # 附着:标点0.6/汉字1.5(行间插入字)
                best, op = prev[j] + (0.6 if is_p else 1.5), 'attach'
            if j >= 1 and cur[j - 1] + 1.3 < best:       # 槽为噪点(划掉的字/污渍)
                best, op = cur[j - 1] + 1.3, 'skip'
            cur[j], cur_bt[j] = best, op
        prev = cur
        bts.append(cur_bt)
    if prev[m] >= INF:
        return None, 0.0
    cost = float(prev[m])
    # 回溯
    pos = [None] * n
    sidx = [None] * n
    i, j = n, m
    while i > 0 or j > 0:
        op = bts[i][j]
        if op == 'take':
            r, x1, x2 = slots[j - 1]
            pos[i - 1] = (r, x1, x2)
            sidx[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif op == 'attach':
            r, x1, x2 = slots[j - 1] if j >= 1 else slots[0]
            w = x2 - x1
            pos[i - 1] = (r, x2 - 0.35 * w, x2 + 0.25 * w)
            sidx[i - 1] = j - 1
            i -= 1
        else:                                            # skip
            j -= 1
    conf = 1.0 - min(1.0, cost / max(1.0, n))
    return pos, sidx, conf


# ---------------- 主类 ----------------
class ManuscriptLocator:
    """v2：ManuscriptLocator.from_text(img, ocr_full_text) —— 推荐入口。
    兼容 v1：ManuscriptLocator(img, transcript_lines) 仍可用（内部并成全文）。"""

    def __init__(self, img_bgr, transcript_lines):
        self._init(img_bgr, ''.join(transcript_lines))

    @classmethod
    def from_text(cls, img_bgr, full_text):
        obj = cls.__new__(cls)
        obj._init(img_bgr, full_text)
        return obj

    def _init(self, img_bgr, full_text):
        self.img = img_bgr
        self.H, self.W = img_bgr.shape[:2]
        self.text = ''.join(full_text.split())          # 去掉全部空白/换行
        self.mask = ink_mask_auto(img_bgr)
        self.rows = detect_rows(self.mask)
        self.pitch = estimate_pitch(self.mask, self.rows)
        slots = []
        for k, (y0, y1) in enumerate(self.rows):
            for x1, x2 in row_slots(self.mask, y0, y1, self.pitch):
                slots.append((k, x1, x2))
        self.pos, self.slot_idx, self.confidence = align_global(list(self.text), slots)

    def locate(self, quote, pad=5, max_local_jumps=None, start=0, end=None):
        """quote → [(x%,y%,w%,h%), ...]；失败返回 []。
        2026-07-08 v2.2:局部置信门槛——引文范围内槽序号若不连续
        (说明该区域有划掉/插字,对齐不可靠),宁可少圈,返回 []。
        2026-07-11 v3:新增 start/end 字符窗口——调用方传入引文所属
        段落在本页文本中的范围,只在窗口内搜索,杜绝"全页找到第一个
        相似位置就画记号"的错位;窗口内精确找不到时做一次近似匹配
        (最长公共子串 ≥ 引文 80% 且 ≥4 字才接受),仍守宁可少圈。"""
        if self.pos is None:
            return []
        q = ''.join(quote.split())
        if not q:
            return []
        lo = max(0, int(start or 0))
        hi = len(self.text) if end is None else min(len(self.text),
                                                    max(lo, int(end)) + len(q))
        p = self.text.find(q, lo, hi)
        if p < 0:
            windowed = (lo > 0 or hi < len(self.text))
            if not windowed:
                return []
            import difflib
            seg = self.text[lo:hi]
            blk = difflib.SequenceMatcher(None, seg, q, autojunk=False)\
                .find_longest_match(0, len(seg), 0, len(q))
            if blk.size < max(4, int(len(q) * 0.8)):
                return []                # 宁可少圈:近似度不够就不上圈
            p = lo + blk.a
            q = q[blk.b:blk.b + blk.size]
        # —— 局部置信:相邻字符槽序号应 +1(附着为 +0) ——
        span_idx = [self.slot_idx[i] for i in range(p, p + len(q))
                    if self.slot_idx[i] is not None]
        if len(span_idx) < max(1, len(q) - 1):
            return []
        jumps = sum(1 for a, b in zip(span_idx, span_idx[1:])
                    if (b - a) not in (0, 1))
        limit = max_local_jumps if max_local_jumps is not None else max(1, len(q) // 4)
        if jumps > limit:
            return []
        # 按行分组
        by_row = {}
        for i in range(p, p + len(q)):
            if self.pos[i] is None:
                continue
            r, x1, x2 = self.pos[i]
            a, b = by_row.get(r, (1e18, -1e18))
            by_row[r] = (min(a, x1), max(b, x2))
        if not by_row:
            return []
        rects = []
        for r in sorted(by_row):
            x1, x2 = by_row[r]
            y0, y1 = self.rows[r]
            rects.append((round(100 * (x1 - pad) / self.W, 2),
                          round(100 * (y0 - pad) / self.H, 2),
                          round(100 * (x2 - x1 + 2 * pad) / self.W, 2),
                          round(100 * (y1 - y0 + 2 * pad) / self.H, 2)))
        return rects

