# -*- coding: utf-8 -*-
"""
transcript_render.py —— 识别稿全文批改渲染器（华文通·改）
================================================================
# 2026-07-07 决策：报告第一页改为“识别稿全文批改”。
# 铁律：引文在原文中找不到逐字匹配 → 该条自动降级到文末“其余批注”，
#       绝不模糊匹配、绝不猜位置（宁可少标，不能标错）。

输入：OCR 全文（字符串，段落用换行分隔）+ 批改标注列表（见 ANNOTATION_SCHEMA）
输出：一张 PNG（排印全文 + 文中红笔直改 + 波浪线佳句 + 编号批注 + 评分）

依赖：Pillow（Streamlit Cloud 已有）。字体传入项目自带的 Noto Sans SC 路径。
"""
import math
from PIL import Image, ImageDraw, ImageFont

RED = (192, 0, 0)
BLACK = (40, 40, 40)
GRAY = (110, 110, 110)

ANNOTATION_SCHEMA = {
    "id": "int，1 起编",
    "category": "错别字|用词不当|语病|标点|用语|佳句|内容",
    "quote": "必须逐字复制自 OCR 原文的连续片段，禁止省略号/改写",
    "context": "可选，quote 前 2-4 个字，用于同串多处出现时消歧；缺省=标注全部出现处",
    "action": "replace（改为 fix）| delete（删去）| praise（佳句波浪线）| note（挂编号，讲解见文末）",
    "fix": "action=replace 时必填",
    "comment": "≤40 字，学生话，先讲为什么再讲怎么改",
}


def _find_spans(paragraphs, ann):
    """在段落列表中找 quote 的全部逐字匹配。返回 [(para_idx, start, end)]。"""
    q = ann.get("quote", "")
    if not q:
        return []
    ctx = ann.get("context", "")
    spans = []
    for pi, p in enumerate(paragraphs):
        start = 0
        while True:
            k = p.find(q, start)
            if k < 0:
                break
            if not ctx or p[max(0, k - len(ctx) - 2):k].find(ctx) >= 0:
                spans.append((pi, k, k + len(q)))
            start = k + 1
    return spans


def _segment(paragraphs, annotations):
    """把每段切成 (text, kind, ann) 片段。kind: 0 正文 / 1 错处 / 3 佳句。
    返回 (segments_per_para, badge_positions, unplaced)。"""
    marks = {pi: [] for pi in range(len(paragraphs))}
    unplaced = []
    for ann in annotations:
        spans = _find_spans(paragraphs, ann)
        if not spans:
            unplaced.append(ann)          # 铁律：找不到 → 降级
            continue
        for (pi, s, e) in spans:
            marks[pi].append((s, e, ann))
    segs_all, badges = [], {}
    for pi, p in enumerate(paragraphs):
        ms = sorted(marks[pi])
        # 去重叠：保留先出现者
        clean, last_end = [], -1
        for s, e, a in ms:
            if s >= last_end:
                clean.append((s, e, a)); last_end = e
        segs, cur = [], 0
        for s, e, a in clean:
            if s > cur:
                segs.append((p[cur:s], 0, None))
            kind = 3 if a["action"] == "praise" else (0 if a["action"] == "note" else 1)
            segs.append((p[s:e], kind, a))
            cur = e
        if cur < len(p):
            segs.append((p[cur:], 0, None))
        segs_all.append(segs)
    return segs_all, unplaced


def render_transcript(essay_text, annotations, out_path,
                      font_regular, font_bold,
                      title="识别稿 · 全文批改", scores=None, review=""):
    paragraphs = [p.strip() for p in essay_text.split("\n") if p.strip()]
    segs_all, unplaced = _segment(paragraphs, annotations)

    W, X0, X1, LH = 1760, 90, 1670, 74
    f_body = ImageFont.truetype(font_regular, 40)
    f_fix = ImageFont.truetype(font_bold, 31)
    f_note = ImageFont.truetype(font_regular, 32)
    f_head = ImageFont.truetype(font_bold, 46)
    f_small = ImageFont.truetype(font_regular, 26)
    f_badge = ImageFont.truetype(font_bold, 30)

    note_anns = [a for a in annotations if a["action"] == "note" and a not in unplaced]

    def draw_all(d=None):
        y = 210
        for segs in segs_all:
            x = X0 + 80
            for text, kind, a in segs:
                # 编号徽章：note 类在片段后挂圈号
                for ch in text:
                    adv = f_body.getlength(ch)
                    if x + adv > X1:
                        x, y = X0, y + LH
                    if d:
                        d.text((x, y), ch, font=f_body,
                               fill=RED if kind in (1, 3) else BLACK)
                        if kind == 1:
                            mid = y + 30
                            d.line([(x - 1, mid), (x + adv + 1, mid)], fill=RED, width=4)
                        if kind == 3:
                            by = y + 56
                            pts = [(x + t, by + 4 * math.sin(t / 7))
                                   for t in range(0, int(adv) + 1, 3)]
                            d.line(pts, fill=RED, width=3)
                    x += adv
                if a and a["action"] == "replace":
                    fx = "→" + a["fix"]
                    for ch in fx:
                        adv = f_fix.getlength(ch)
                        if x + adv > X1:
                            x, y = X0, y + LH
                        if d:
                            d.text((x, y + 10), ch, font=f_fix, fill=RED)
                        x += adv
                    x += 6
                if a and a["action"] == "delete":
                    for ch in "（删）":
                        adv = f_fix.getlength(ch)
                        if x + adv > X1:
                            x, y = X0, y + LH
                        if d:
                            d.text((x, y + 10), ch, font=f_fix, fill=RED)
                        x += adv
                if a and a["action"] == "note":
                    n = str(note_anns.index(a) + 1) if a in note_anns else "?"
                    r = 24
                    if x + 2 * r > X1:
                        x, y = X0, y + LH
                    if d:
                        cx, cy = x + r, y + 26
                        for i in range(3):
                            d.ellipse([cx - r - i, cy - r - i, cx + r + i, cy + r + i], outline=RED)
                        tb = d.textbbox((0, 0), n, font=f_badge)
                        d.text((cx - (tb[2] - tb[0]) / 2, cy - (tb[3] - tb[1]) / 2 - tb[1]),
                               n, font=f_badge, fill=RED)
                    x += 2 * r + 10
            y += LH + 26
        return y

    def flow_text(d, text, x0, y, font, fill):
        x = x0
        for ch in text:
            a = font.getlength(ch)
            if x + a > X1:
                x, y = x0, y + 48
            if d:
                d.text((x, y), ch, font=font, fill=fill)
            x += a
        return y + 62

    end_y = draw_all(None)
    y_est = end_y + 200
    for i, a in enumerate(note_anns, 1):
        y_est = flow_text(None, f"① {a['comment']}", X0 + 40, y_est, f_note, RED)
    for a in unplaced:
        y_est = flow_text(None, a.get("comment", ""), X0 + 40, y_est, f_note, RED)
    H = y_est + 460

    cv = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(cv)
    d.text((X0, 50), title, font=f_head, fill=BLACK)
    d.text((X0, 130), "程序排印，据 AI 识别整理；如与手写原稿有出入，以原稿为准。"
                      "红色删除线＝改错，波浪线＝佳句，①②＝见文末批注。",
           font=f_small, fill=GRAY)
    end_y = draw_all(d)

    y = end_y + 40
    d.line([(X0, y), (X1, y)], fill=(200, 200, 200), width=2); y += 40
    d.text((X0, y), "批注", font=ImageFont.truetype(font_bold, 38), fill=RED); y += 70
    CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫"
    for i, a in enumerate(note_anns):
        y = flow_text(d, f"{CIRCLED[i]} {a['comment']}", X0 + 40, y, f_note, RED)
    if unplaced:
        y += 10
        d.text((X0 + 40, y), "其余批注（原文中未能逐字定位，仅列于此）：", font=f_small, fill=GRAY)
        y += 46
        for a in unplaced:
            y = flow_text(d, f"· [{a['category']}] {a.get('quote','')}：{a.get('comment','')}",
                          X0 + 40, y, f_note, RED)

    if scores:
        y += 20
        d.line([(X0, y), (X1, y)], fill=(200, 200, 200), width=2); y += 40
        fb = ImageFont.truetype(font_bold, 40)
        d.text((X0, y), f"内容 {scores['content']}/30（{scores['content_band']}）   "
                        f"语文 {scores['language']}/30（{scores['language_band']}）   "
                        f"总分 {scores['total']}/60   等级 {scores['grade']}",
               font=fb, fill=RED); y += 90
        if review:
            flow_text(d, "总评：" + review, X0, y, f_note, BLACK)

    cv.save(out_path)
    return out_path

