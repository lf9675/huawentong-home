# -*- coding: utf-8 -*-
"""Fallback line transcription and measured region localization.

Rows are detected independently and transcribed with the configured vision API.
Text must match uniquely, including every supplied anchor. Grid/ink slots are
not reliable character boundaries; return line regions, never synthetic glyph
boxes. Calls are cached per canonical image. Failed rows remain explicit.
"""
import base64
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
import requests

from manuscript_locator import (ink_mask_auto, detect_rows,
                                estimate_pitch, row_slots)

MODEL = "glm-4v-flash"
MAX_WORKERS = 4
CALL_TIMEOUT = 45             # 单行调用超时(秒)
EMPTY_ROW_LIMIT = 0.5         # 超过一半的行转写为空 → 判定整页失败
TRANSCRIPT_VERSION = 3  # Reject giant regions and invalidate old cached transcripts.

ROW_PROMPT = (
    "这是一张作文方格纸上裁出来的【一行】手写汉字。"
    "请从左到右转写这一行的文字,包括标点。"
    "只输出文字本身,不要任何解释、引号或标签。"
    "写了什么就转写什么,包括错别字也照原样转写,不要改正。"
    "如果这一行是空白或者只有格线,输出【空】。"
)


def _n(s):
    """归一化:去掉全部空白(与旧 locator 口径一致)"""
    return ''.join((s or '').split())


def img_hash(img_bytes):
    """图片字节 → 缓存键"""
    return hashlib.md5(img_bytes).hexdigest()


def _b64_jpg(img):
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise RuntimeError("row crop encode failed")
    return base64.b64encode(buf.tobytes()).decode()


def _read_row(row_img, api_key, base_url):
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": "data:image/jpeg;base64," + _b64_jpg(row_img)}},
                {"type": "text", "text": ROW_PROMPT},
            ],
        }],
        "temperature": 0.1,
    }
    r = requests.post(base_url.rstrip("/") + "/api/paas/v4/chat/completions",
                      json=payload, timeout=CALL_TIMEOUT,
                      headers={"Authorization": f"Bearer {api_key}"})
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"].strip()
    return "" if ("【空】" in txt or txt == "空") else txt


def transcribe_page(img_bgr, api_key, base_url="https://open.bigmodel.cn"):
    """整页 → {'rows':[(y0,y1)..], 'texts':[..], 'slots':[[(x1,x2)..]..], 'pitch':f}
    返回 None 表示整页失败(调用方不画记号)。全程不抛异常。"""
    try:
        H, W = img_bgr.shape[:2]
        mask = ink_mask_auto(img_bgr)
        rows = detect_rows(mask)
        # Desk texture and sideways photos can merge hundreds of pixels into one
        # supposed line. Do not send those regions to row OCR as if they were lines.
        rows = [(a, b) for a, b in rows if 8 <= b-a <= H*0.10]
        if not rows:
            return None
        pitch = estimate_pitch(mask, rows)
        slots_all = [row_slots(mask, y0, y1, pitch) for (y0, y1) in rows]
        crops = [img_bgr[max(0, y0 - 6):min(H, y1 + 6), :] for (y0, y1) in rows]

        def _safe(c):
            try:
                return _read_row(c, api_key, base_url)
            except Exception:
                return ""            # 单行失败只丢这一行,不影响其他行

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            texts = list(ex.map(_safe, crops))

        n_empty = sum(1 for t in texts if not _n(t))
        if len(texts) == 0 or n_empty / len(texts) > EMPTY_ROW_LIMIT:
            return None              # 大面积转写失败 → 整页放弃,宁可不画
        return {
                "version": TRANSCRIPT_VERSION,
                "width": int(W),
                "height": int(H),
                "rows": [list(r) for r in rows],
                "texts": texts,
                "slots": [[list(s) for s in sl] for sl in slots_all],
                "pitch": float(pitch),
                "failed_rows": [i for i, t in enumerate(texts) if not _n(t)],
        }
    except Exception:
        return None


class RowLocator:
    """基于逐行转写结果的定位器。transcript 可来自 transcribe_page
    或会话缓存(JSON 可序列化,st.session_state 直接存取)。"""

    def __init__(self, transcript):
        self.t = transcript
        self.W = int(transcript.get("width") or 0)
        self.H = int(transcript.get("height") or 0)
        if self.W <= 0 or self.H <= 0:
            raise ValueError("row transcript missing image width/height; rebuild cache")
        self.texts_n = [_n(x) for x in transcript["texts"]]
        # 全页拼接文本 + 每行起始偏移(跨行引文用)
        self.offsets, pos = [], 0
        for tn in self.texts_n:
            self.offsets.append(pos)
            pos += len(tn)
        self.full = ''.join(self.texts_n)

    # ---------- 内部:全页文本内找引文起点 ----------
    def _find(self, qn, a_left, a_right):
        from annotation_core import unique_span
        span, _ = unique_span(self.full, qn, a_left, a_right)
        return span[0] if span else None

    def locate_source(self, source, start, end):
        from annotation_core import norm, unique_span
        source = norm(source)
        if source == self.full:
            span = (start, end)
        else:
            span, _ = unique_span(self.full, source[start:end],
                                  source[max(0, start-6):start], source[end:end+6])
        if span is None:
            return None
        rects, covered = [], 0
        for k, offset in enumerate(self.offsets):
            lo, hi = max(span[0], offset), min(span[1], offset + len(self.texts_n[k]))
            if lo >= hi:
                continue
            slots = self.t['slots'][k]
            if not slots:
                return None
            # Ink slots are not verified characters. Mark the whole measured row.
            x1, x2 = min(s[0] for s in slots), max(s[1] for s in slots)
            y1, y2 = self.t['rows'][k]
            rects.append([100*x1/self.W, 100*y1/self.H,
                          100*(x2-x1)/self.W, 100*(y2-y1)/self.H])
            covered += hi-lo
        return {'rects': rects, 'precision': 'region'} if covered == end-start else None

    def _row_of(self, gpos):
        """全页偏移 → (行号, 行内偏移)"""
        for k in range(len(self.offsets) - 1, -1, -1):
            if gpos >= self.offsets[k]:
                return k, gpos - self.offsets[k]
        return 0, gpos

    def locate(self, quote, a_left="", a_right=""):
        start = self._find(_n(quote), _n(a_left), _n(a_right))
        result = self.locate_source(self.full, start, start + len(_n(quote))) if start is not None else None
        return result['rects'] if result else []


def build_row_locators(page_bytes_list, api_key, base_url, cache=None):
    """为每页构建 RowLocator;cache 传 st.session_state 即可跨重渲染复用。
    单页失败返回 None 占位,整体永不抛异常。"""
    out = []
    for bs in page_bytes_list:
        try:
            key = "rowloc_" + img_hash(bs)
            tr = cache.get(key) if cache is not None else None
            # v1 cache lacked image width/height and returned pixel x1/y1/x2/y2.
            # Never reuse it after the coordinate-contract fix.
            if tr is not None and int(tr.get("version") or 0) != TRANSCRIPT_VERSION:
                tr = None
            if tr is None:
                im = cv2.imdecode(np.frombuffer(bs, np.uint8), cv2.IMREAD_COLOR)
                tr = transcribe_page(im, api_key, base_url) if im is not None else None
                if tr is not None and cache is not None:
                    cache[key] = tr
            out.append(RowLocator(tr) if tr else None)
        except Exception:
            out.append(None)
    return out

