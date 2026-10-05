# -*- coding: utf-8 -*-
"""
pdf_report.py — 华文通·改 学习报告 PDF 导出
════════════════════════════════════════════
- 依赖: reportlab (requirements.txt 需加 reportlab)
- 字体: fonts/NotoSansSC-Regular.ttf + fonts/NotoSansSC-Bold.ttf
        (开源 OFL 授权,可随仓库分发;缺字体时抛 RuntimeError,由调用方兜底)
- 入口: build_pdf_report(fb, name, exam_level_cfg, genre, prompt_title) -> bytes
- 设计原则: 生成失败绝不影响结果页 — 调用处必须 try/except
- 2026-07-06: 新增实用文支持 — format_check 格式清单渲染 + 实用文句子功能标签配色
"""

import io
import os
import re
from datetime import datetime, timezone, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── 品牌色(与网页一致) ─────────────────────────────
INK = HexColor("#1a1a2e")
NAVY = HexColor("#0f3460")
GOLD = HexColor("#f0c27f")
GOLD_DARK = HexColor("#7a5c1e")
CREAM = HexColor("#fdf8ee")
GRAY_BG = HexColor("#f5f4f0")
RED_BANNER = HexColor("#8e2020")
BLUE_TIER = HexColor("#1565c0")
BLUE_BG = HexColor("#e3f2fd")
RED_TIER = HexColor("#c62828")
RED_BG = HexColor("#fdecea")
TEXT = HexColor("#2c2c2a")
MUTED = HexColor("#888888")
GREEN_OK = HexColor("#2e7d32")

# 句子功能标签配色 — 必须与 student.py 的 _STRUCT_TAG_COLORS 保持一致
STRUCT_TAG_COLORS = {
    # 议论文 PEEL
    "论点": "#c62828", "解释": "#ef6c00", "举例": "#2e7d32",
    "分析": "#1565c0", "扣题": "#6a1b9a",
    # 记叙文
    "铺垫": "#5d4037", "环境": "#00695c", "动作": "#2e7d32",
    "心理": "#1565c0", "对话": "#ef6c00", "细节": "#c62828",
    "抒情": "#6a1b9a", "点题": "#8e24aa",
    # 实用文(电邮/论坛,2026-07-06 新增)
    "问候": "#00695c", "身份": "#5d4037", "目的": "#c62828",
    "回应": "#ef6c00", "观点": "#1565c0", "原因": "#2e7d32",
    "建议": "#6a1b9a", "结束": "#8e24aa",
}

_FONTS_REGISTERED = False


def _register_fonts():
    """注册中文字体;找不到字体文件时抛 RuntimeError"""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    reg = os.path.join(base, "NotoSansSC-Regular.ttf")
    bold = os.path.join(base, "NotoSansSC-Bold.ttf")
    if not os.path.exists(reg):
        raise RuntimeError(f"缺少中文字体文件: {reg}")
    pdfmetrics.registerFont(TTFont("NotoSC", reg))
    pdfmetrics.registerFont(TTFont("NotoSC-Bold", bold if os.path.exists(bold) else reg))
    _FONTS_REGISTERED = True


# ── 文本工具 ───────────────────────────────────────

def _esc(s):
    """XML 转义(reportlab Paragraph 内联标记是 XML)"""
    return (str(s or "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _tagged(text):
    """把示范文字里的【功能标签】转成彩色内联标记;未知【】原样保留"""
    esc = _esc(text)

    def _rep(m):
        tag = m.group(1)
        color = STRUCT_TAG_COLORS.get(tag)
        if not color:
            return m.group(0)
        return (f'<font name="NotoSC-Bold" color="{color}" size="7.5"> {tag} </font>')

    return re.sub(r"【([^【】]{1,6})】", _rep, esc)


def _has_struct_tags(text):
    for m in re.finditer(r"【([^【】]{1,6})】", str(text or "")):
        if m.group(1) in STRUCT_TAG_COLORS:
            return True
    return False


# ── 样式 ───────────────────────────────────────────

def _styles():
    def s(name, **kw):
        base = dict(fontName="NotoSC", fontSize=9.5, leading=17,
                    textColor=TEXT, wordWrap="CJK")
        base.update(kw)
        return ParagraphStyle(name, **base)

    return {
        "h_title": s("h_title", fontName="NotoSC-Bold", fontSize=16,
                     leading=22, textColor=INK),
        "h_sub": s("h_sub", fontSize=8.5, leading=13, textColor=MUTED),
        "h_sec": s("h_sec", fontName="NotoSC-Bold", fontSize=11.5,
                   leading=18, textColor=NAVY, spaceBefore=6),
        "body": s("body"),
        "body_small": s("body_small", fontSize=8.8, leading=15.5),
        "orig": s("orig", fontSize=8.8, leading=15.5, textColor=HexColor("#555555")),
        "score_num": s("score_num", fontName="NotoSC-Bold", fontSize=17,
                       leading=20, alignment=TA_CENTER, textColor=INK),
        "score_lbl": s("score_lbl", fontSize=8, leading=11,
                       alignment=TA_CENTER, textColor=MUTED),
        "banner_t": s("banner_t", fontName="NotoSC-Bold", fontSize=8.5,
                      leading=12, textColor=HexColor("#ffd9b3")),
        "banner_b": s("banner_b", fontName="NotoSC-Bold", fontSize=10,
                      leading=16, textColor=HexColor("#ffffff")),
        "tier_lbl": s("tier_lbl", fontName="NotoSC-Bold", fontSize=9, leading=13),
        "footer": s("footer", fontSize=7.5, leading=10, textColor=MUTED,
                    alignment=TA_CENTER),
        # 2026-07-06 新增:格式清单表格用
        "fmt_cell": s("fmt_cell", fontSize=8.5, leading=13),
        "fmt_head": s("fmt_head", fontName="NotoSC-Bold", fontSize=8,
                      leading=11, textColor=MUTED),
    }


def _box(inner, bg, border=None, pad=6):
    """把一组 flowable 装进带底色/边框的单格表格 = 圆角卡片的 PDF 近似"""
    t = Table([[inner]], colWidths=[None])
    style = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), pad + 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad + 2),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
    ]
    if border:
        style.append(("LINEBEFORE", (0, 0), (0, -1), 2.2, border))
    t.setStyle(TableStyle(style))
    return t


# ── 实用文格式清单(2026-07-06 新增) ─────────────────

def _format_check_section(fmt_checks, st, doc_width):
    """把 AI 返回的 format_check 数组渲染成格式清单表格。
    返回 flowable 列表;数据为空或非法时返回 []。绝不抛异常。"""
    try:
        if not isinstance(fmt_checks, list) or not fmt_checks:
            return []
        rows = [[Paragraph("项目", st["fmt_head"]),
                 Paragraph("状态", st["fmt_head"]),
                 Paragraph("扣分", st["fmt_head"]),
                 Paragraph("说明", st["fmt_head"])]]
        ded_total = 0
        for fc in fmt_checks:
            if not isinstance(fc, dict):
                continue
            item = _esc(fc.get("item", ""))
            status = _esc(fc.get("status", ""))
            try:
                ded = int(float(fc.get("deduction", 0) or 0))
            except Exception:
                ded = 0
            note = _esc(fc.get("note", ""))
            ded_total += max(ded, 0)
            ok = ded <= 0
            icon = "✓" if ok else "✕"
            color = "#2e7d32" if ok else "#c62828"
            ded_txt = f'<font color="#c62828">−{ded}</font>' if ded > 0 else "—"
            rows.append([
                Paragraph(f'<font color="{color}" name="NotoSC-Bold">{icon}</font> {item}',
                          st["fmt_cell"]),
                Paragraph(f'<font color="{color}">{status}</font>', st["fmt_cell"]),
                Paragraph(ded_txt, st["fmt_cell"]),
                Paragraph(note, st["fmt_cell"]),
            ])
        if len(rows) <= 1:
            return []
        tbl = Table(rows, colWidths=[doc_width * 0.20, doc_width * 0.22,
                                     doc_width * 0.10, doc_width * 0.48])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), GRAY_BG),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, HexColor("#e8e0d5")),
            ("BOX", (0, 0), (-1, -1), 0.6, GOLD),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        sum_txt = (f"共扣 {ded_total} 分" if ded_total > 0 else "格式全部正确,没有扣分")
        out = [Paragraph(f"实用文格式清单 · {sum_txt}", st["h_sec"]),
               Spacer(1, 3), tbl, Spacer(1, 2),
               Paragraph("格式类扣分计入「语文与结构」(合计最多扣 2 分);"
                         "漏回应网民的扣分计入「内容」。", st["h_sub"]),
               Spacer(1, 8)]
        return out
    except Exception:
        return []


# ── 主入口 ─────────────────────────────────────────

def build_pdf_report(fb, name, exam_level_cfg, genre="", prompt_title=""):
    """
    fb              : AI 批改结果 dict (feedback)
    name            : 学生昵称
    exam_level_cfg  : dict, 需含 name / content_max / language_max / essay_total
    genre           : 文体
    prompt_title    : 题目
    返回            : PDF bytes
    """
    _register_fonts()
    st = _styles()

    max_c = exam_level_cfg.get("content_max", 30)
    max_l = exam_level_cfg.get("language_max", 30)
    max_t = exam_level_cfg.get("essay_total", max_c + max_l)
    level_name = exam_level_cfg.get("name", "")

    scores = fb.get("scores", {}) or {}
    c_score = scores.get("content", 0)
    l_score = scores.get("language", 0)
    t_score = scores.get("total", c_score + l_score)
    grade = fb.get("grade_estimate", "") or "—"
    grade_distance = fb.get("grade_distance", "")
    strengths = fb.get("strengths", []) or []
    overall = fb.get("overall_suggestion", "") or ""
    coaching = fb.get("coaching_advice", []) or []
    paragraphs = fb.get("paragraph_feedback", []) or []

    sg_now = datetime.now(timezone(timedelta(hours=8)))
    date_str = sg_now.strftime("%Y-%m-%d")

    buf = io.BytesIO()
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=14 * mm, bottomMargin=16 * mm,
        title=f"华文通·改 学习报告 {date_str}", author="华文通·改",
    )

    def _footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("NotoSC", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(
            A4[0] / 2, 9 * mm,
            f"华文通·改 CLever · AI 批改学习报告 · 仅供学习参考 · 第 {_doc.page} 页")
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame],
                                       onPage=_footer)])

    story = []

    # ── 1. 报告头 ──
    meta_bits = [b for b in [level_name, genre, date_str] if b]
    story.append(Paragraph(f"{_esc(name)} 的作文学习报告", st["h_title"]))
    story.append(Paragraph(
        " ｜ ".join(meta_bits) + " ｜ 基于新加坡考评局(SEAB)官方评分标准",
        st["h_sub"]))
    if prompt_title:
        story.append(Spacer(1, 2))
        story.append(Paragraph(f"题目:{_esc(prompt_title)}", st["h_sub"]))
    story.append(Spacer(1, 6))

    # ── 2. 分数卡(四列表格) ──
    def _score_cell(label, num, denom):
        return [Paragraph(label, st["score_lbl"]),
                Paragraph(f"{num}<font size=9 color=#888888>/{denom}</font>",
                          st["score_num"])]

    grade_cell = [Paragraph("预估等级", st["score_lbl"]),
                  Paragraph(f'<font color="#7a5c1e">{_esc(grade)}</font>',
                            st["score_num"])]
    score_tbl = Table(
        [[_score_cell("内容", c_score, max_c),
          _score_cell("语文", l_score, max_l),
          _score_cell("总分", t_score, max_t),
          grade_cell]],
        colWidths=[doc.width / 4.0] * 4)
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (2, 0), GRAY_BG),
        ("BACKGROUND", (3, 0), (3, 0), CREAM),
        ("BOX", (3, 0), (3, 0), 0.8, GOLD),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, HexColor("#e8e0d5")),
        ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#e8e0d5")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(score_tbl)
    if grade_distance:
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"{_esc(grade_distance)}", st["body_small"]))
    story.append(Spacer(1, 8))

    # ── 3. 最影响分数的问题 ──
    top = fb.get("top_issue") or {}
    tp_problem = top.get("problem", "")
    tp_idx = top.get("para_index")
    if tp_problem:
        loc = f"第 {tp_idx} 段:" if tp_idx else ""
        banner = _box(
            [Paragraph("★ 最影响你分数的一个问题", st["banner_t"]),
             Paragraph(f"{_esc(loc)}{_esc(tp_problem)}", st["banner_b"])],
            bg=RED_BANNER, pad=7)
        story.append(banner)
        story.append(Spacer(1, 8))

    # ── 3.5 实用文格式清单(2026-07-06 新增,作文批改无此字段自动跳过) ──
    fmt_flow = _format_check_section(fb.get("format_check"), st, doc.width)
    if fmt_flow:
        story.append(KeepTogether(fmt_flow))

    # ── 4. 老师总评 ──
    sec = [Paragraph("老师总评", st["h_sec"]), Spacer(1, 3)]
    if strengths:
        sec.append(Paragraph(
            "<font name='NotoSC-Bold'>你的优点:</font>" +
            _esc(";".join(strengths)), st["body"]))
        sec.append(Spacer(1, 3))
    # 2026-07-12 决策:记叙文总评含选材点评(其他文体该字段为空,自动跳过)
    _mat_rev = fb.get("material_review", "") or ""
    if _mat_rev:
        sec.append(Paragraph(
            "<font name='NotoSC-Bold'>选材点评:</font>" + _esc(_mat_rev),
            st["body"]))
        sec.append(Spacer(1, 3))
    if overall:
        sec.append(Paragraph(
            "<font name='NotoSC-Bold'>最重要的建议:</font>" + _esc(overall),
            st["body"]))
        sec.append(Spacer(1, 3))
    for i, c in enumerate(coaching, 1):
        sec.append(Paragraph(f"{i}. {_esc(c)}", st["body_small"]))
    story.append(KeepTogether(sec))
    story.append(Spacer(1, 10))

    # ── 5. 逐段批改 ──
    if paragraphs:
        story.append(Paragraph("逐段批改与示范", st["h_sec"]))
        story.append(Paragraph(
            "彩色小字 = 这个句子在段落里的作用(如 论点/解释/举例/分析/扣题)",
            st["h_sub"]))
        story.append(Spacer(1, 5))

    for p_idx, p in enumerate(paragraphs):
        para_num = p.get("para_num", p_idx + 1)
        para_role = p.get("para_role", "")
        original = p.get("original_text", "")
        why = p.get("why_and_how", "")
        highlights = p.get("highlights", "")
        rev_i = p.get("revised_improved") or p.get("revised_advanced") or ""
        rev_t = p.get("revised_top") or ""

        head = Paragraph(
            f"<font name='NotoSC-Bold' color='#0f3460'>"
            f"第 {para_num} 段 · {_esc(para_role)}</font>", st["body"])
        blocks = [head, Spacer(1, 3)]

        if original:
            blocks.append(_box(
                [Paragraph("你写的", st["score_lbl"]),
                 Paragraph(_esc(original), st["orig"])],
                bg=GRAY_BG, border=HexColor("#cccccc")))
            blocks.append(Spacer(1, 4))

        why_parts = []
        if highlights:
            why_parts.append(Paragraph("★ 写得好: " + _esc(highlights), st["body_small"]))
        if why:
            why_parts.append(Paragraph(
                "<font name='NotoSC-Bold'>为什么要改?怎么改?</font> " +
                _esc(why), st["body_small"]))
        if why_parts:
            blocks.append(_box(why_parts, bg=HexColor("#fdf8ee"), border=GOLD))
            blocks.append(Spacer(1, 4))

        # 段头 + 原文 + 讲解尽量不跨页;示范版本较长,单独成块
        story.append(KeepTogether(blocks))

        if rev_i:
            story.append(_box(
                [Paragraph('<font color="#1565c0">● 提升版 · 把缺的东西补齐</font>',
                           st["tier_lbl"]),
                 Paragraph(_tagged(rev_i), st["body_small"])],
                bg=BLUE_BG, border=BLUE_TIER))
            story.append(Spacer(1, 4))
        if rev_t:
            story.append(_box(
                [Paragraph('<font color="#c62828">● 高分版 · 冲 A1 的写法</font>',
                           st["tier_lbl"]),
                 Paragraph(_tagged(rev_t), st["body_small"])],
                bg=RED_BG, border=RED_TIER))
        story.append(Spacer(1, 12))

    # ── 2026-07-13 决策:信任机制①——报告末尾加批改透明说明,
    #    告诉家长/老师"评分依据可核验、识别有错可更正重批" ──
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "批改说明:本报告由 AI 按 SEAB 官方评分标准逐项对照生成,"
        "「评分依据」部分引用官方档位描述,欢迎家长与老师对照核验;"
        "如文字识别与作文原文有出入,可在线上批改页更正后重批一次。",
        st["footer"]))

    doc.build(story)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════
# 2026-07-12:左图右评版学习报告(方案A — 批改当次会话内生成)
# 数据源: image_review_page.build_annotated_pages_for_pdf()
# 版式: 横向 A4;每张作文照片一页,左=画好记号的照片,右=该页段落评语
#       首页顶部含 分数条+最大问题;失败绝不影响结果页(调用方 try/except)
# ═══════════════════════════════════════════════════════════
def build_image_pdf_report(annotated_pages, fb, name, exam_level_cfg,
                           genre="", prompt_title=""):
    """annotated_pages: [{'image_jpg': bytes, 'para_cards': [...]}, ...]"""
    from reportlab.lib.pagesizes import landscape
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas as _canvas

    _register_fonts()
    PAGE_W, PAGE_H = landscape(A4)          # 842 x 595 pt
    M = 12 * mm
    buf = io.BytesIO()
    c = _canvas.Canvas(buf, pagesize=landscape(A4))

    scores = fb.get('scores') or {}
    total = scores.get('total', '')
    max_total = exam_level_cfg.get('total_max', 60)
    _sgt = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%Y-%m-%d')

    def _wrap(text, font, size, width):
        """按像素宽度折行(中文逐字折)。"""
        out, line = [], ''
        for ch in str(text or ''):
            if ch == '\n':
                out.append(line); line = ''
                continue
            if pdfmetrics.stringWidth(line + ch, font, size) > width:
                out.append(line); line = ch
            else:
                line += ch
        if line:
            out.append(line)
        return out

    for pi, page in enumerate(annotated_pages):
        top_y = PAGE_H - M
        # ── 首页页眉:标题 + 分数 + 最大问题 ──
        if pi == 0:
            c.setFont("NotoSC-Bold", 13)
            c.setFillColor(HexColor("#2c2c2a"))
            _title = f"CLever · 华文通 学习报告 — {name}"
            if prompt_title:
                _title += f" · {prompt_title[:22]}"
            c.drawString(M, top_y - 12, _title)
            c.setFont("NotoSC-Bold", 13)
            c.setFillColor(HexColor("#b3541e"))
            c.drawRightString(PAGE_W - M, top_y - 12,
                              f"{total} / {max_total}　{_sgt}")
            top_y -= 22
            _ti = fb.get('top_issue') or {}
            _tp = _ti.get('problem') if isinstance(_ti, dict) else ''
            if _tp:
                c.setFont("NotoSC", 9)
                c.setFillColor(HexColor("#8a2c0d"))
                for ln in _wrap(f"最影响分数的一个问题:{_tp}",
                                "NotoSC", 9, PAGE_W - 2 * M)[:2]:
                    c.drawString(M, top_y - 10, ln)
                    top_y -= 13
            top_y -= 4

        # ── 左:批注照片(等比缩放,占页宽 55%)──
        img = ImageReader(io.BytesIO(page['image_jpg']))
        iw, ih = img.getSize()
        box_w = (PAGE_W - 2 * M) * 0.55
        box_h = top_y - M
        scale = min(box_w / iw, box_h / ih)
        dw, dh = iw * scale, ih * scale
        c.drawImage(img, M, top_y - dh, width=dw, height=dh,
                    preserveAspectRatio=True, anchor='nw')
        c.setFont("NotoSC", 7.5)
        c.setFillColor(HexColor("#888888"))
        # 2026-07-12:字级圈画暂停时照片上没有记号,页脚不再显示记号说明
        # 2026-07-13 决策:信任机制④——如实说明"覆盖优先"策略的取舍,
        # 记号可能略偏不隐瞒,引导以评语文字为准
        _legend = ("　·　记号说明:红色=已定位　黄色范围=待确认　完整问题见后附清单"
                   ""
                   if page.get('hotspots') else "")
        c.drawString(M, M - 6, f"第 {pi + 1} 页{_legend}")

        # ── 右:该页段落评语 ──
        rx = M + box_w + 8 * mm
        rw = PAGE_W - M - rx
        y = top_y - 4
        cards = page.get('para_cards') or []
        if not cards:
            c.setFont("NotoSC", 9)
            c.setFillColor(HexColor("#666666"))
            c.drawString(rx, y - 10, "本页没有单独的段落评语。")
        for card in cards:
            if y < M + 40:
                c.setFont("NotoSC", 8)
                c.setFillColor(HexColor("#888888"))
                c.drawString(rx, M + 6, "…评语较长,完整内容见线上批改页。")
                break
            c.setFont("NotoSC-Bold", 10)
            c.setFillColor(HexColor("#1f4e79"))
            c.drawString(rx, y - 11,
                         f"第 {card.get('n', '?')} 段 · {card.get('title', '')}"[:34])
            y -= 17
            c.setFillColor(HexColor("#2c2c2a"))
            c.setFont("NotoSC", 8.5)
            for key, label in (('comment', ''), ('howto', '怎么改:')):
                txt = card.get(key) or ''
                if not txt:
                    continue
                for ln in _wrap(label + txt, "NotoSC", 8.5, rw)[:6]:
                    if y < M + 24:
                        break
                    c.drawString(rx, y - 10, ln)
                    y -= 12
                y -= 3
            y -= 6
        c.showPage()

    # Full ledger appendix: never omit unlocated findings or truncate long notes.
    issues = [a for page in annotated_pages for a in page.get('issues', [])]
    if issues:
        statuses = {'located':'已定位', 'manual':'人工定位', 'approximate':'范围待确认',
                    'unlocated':'待定位', 'uncertain':'字迹待核对', 'dismissed':'已取消'}
        def ledger_header():
            c.setFont("NotoSC-Bold", 12)
            c.setFillColor(HexColor("#20304a"))
            c.drawString(M, PAGE_H-M-12, "完整问题清单（包括待定位项目）")
        ledger_header()
        y = PAGE_H-M-38
        for a in issues:
            text = (f"{a['n']}. [{statuses.get(a['status'], a['status'])}] {a['cat']}\n"
                    f"原文：{a['quote']}\n修改：{a['fix']}\n原因：{a['why']}")
            for ln in _wrap(text, "NotoSC", 10, PAGE_W-2*M):
                if y < M+16:
                    c.showPage(); ledger_header(); y = PAGE_H-M-38
                c.setFont("NotoSC", 10)
                c.drawString(M, y, ln)
                y -= 16
            y -= 10
        c.showPage()

    # ── 末页:总评 + 教练建议(纯文字,复用简单排版)──
    c.setFont("NotoSC-Bold", 12)
    c.setFillColor(HexColor("#2c2c2a"))
    c.drawString(M, PAGE_H - M - 12, "老师总评与练习建议")
    y = PAGE_H - M - 34
    c.setFont("NotoSC", 9.5)
    blocks = []
    if fb.get('material_review'):    # 2026-07-12:记叙文选材点评(其他文体为空自动跳过)
        blocks.append("选材点评:" + str(fb['material_review']))
    if fb.get('overall_suggestion'):
        blocks.append("最重要的一条:" + str(fb['overall_suggestion']))
    for i, adv in enumerate((fb.get('coaching_advice') or [])[:3]):
        blocks.append(f"建议{i + 1}:{adv}")
    if fb.get('encouragement'):
        blocks.append("老师想对你说:" + str(fb['encouragement']))
    for b in blocks:
        for ln in _wrap(b, "NotoSC", 9.5, PAGE_W - 2 * M):
            if y < M + 12:
                break
            c.drawString(M, y, ln)
            y -= 14
        y -= 8
    c.showPage()
    c.save()
    return buf.getvalue()

