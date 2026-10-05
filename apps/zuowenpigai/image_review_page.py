# -*- coding: utf-8 -*-
"""Photo review and PDF share a lossless, strictly anchored annotation ledger.

Only provider character boxes and teacher-confirmed geometry are rendered as
precise marks. Region-only coordinates remain visible as pending regions.
"""
import traceback
import streamlit as st
import streamlit.components.v1 as components

CONF_THRESHOLD = 0.75  # Retained for caller compatibility; no longer a precision gate.
ENABLE_HOTSPOTS = True
HOTSPOT_BACKEND = "row"
DEBUG = False


def _norm(s):
    return ''.join((s or '').split())


# ---------------- 最大问题 ----------------
def _build_top_issue(fb):
    paragraphs = fb.get('paragraph_feedback') or []
    t = fb.get('top_issue') or {}
    title, fix = '', ''
    if isinstance(t, dict) and t.get('problem'):
        title = str(t['problem'])
        try:
            pi = int(t.get('para_index', 0)) - 1        # AI 用 1 起始
        except Exception:
            pi = -1
        if 0 <= pi < len(paragraphs):
            struct = paragraphs[pi].get('structure_content_issues') or []
            if struct:
                fix = struct[0].get('suggestion', '') or ''
            title = f"第 {paragraphs[pi].get('para_num', pi + 1)} 段：{title}"
    if not title:
        for p_idx, p in enumerate(paragraphs):
            struct = p.get('structure_content_issues') or []
            if struct:
                title = f"第 {p.get('para_num', p_idx + 1)} 段：{struct[0].get('problem', '')}"
                fix = struct[0].get('suggestion', '') or ''
                break
    impact = fb.get('grade_distance', '') or '改好这一处，分数提升最快。'
    return dict(title=title or (fb.get('overall_suggestion', '') or '')[:60],
                impact=impact, fix=fix)


# ---------------- 段落卡 ----------------
def _card_from_para(p, p_idx):
    struct = p.get('structure_content_issues') or []
    comment = (p.get('why_and_how')
               or (struct[0].get('problem', '') if struct else '')
               or p.get('highlights', ''))
    return dict(
        n=p.get('para_num', p_idx + 1),
        title=p.get('para_role') or f"第{p_idx + 1}段",
        comment=comment,
        improved='',   # 2026-07-12 决策:提升版停用(prompt 已不再输出),右栏只出高分版
        top=p.get('revised_top') or p.get('revised_advanced', ''),
        howto=(struct[0].get('suggestion', '') if struct else ''),
    )


# ---------------- 组装每页数据 ----------------
def _build_pages(fb, locators, page_bytes_b64, page_mimes, page_texts,
                 row_locs=None, layout_locs=None):
    from annotation_core import build_ledger, apply_overrides, ledger_pages, source_version
    count = len(page_texts)
    sources = [[layout_locs[i] if layout_locs and i < len(layout_locs) else None,
                row_locs[i] if row_locs and i < len(row_locs) else None] for i in range(count)]
    ledger = build_ledger(fb, page_texts, sources)
    ledger = apply_overrides(ledger, fb.get('annotation_overrides'), count, source_version(page_texts))
    pages = ledger_pages(ledger, count)
    from annotation_core import norm, unique_span
    bounds = [0]
    for text in page_texts:
        bounds.append(bounds[-1] + len(norm(text)))
    full = ''.join(norm(t) for t in page_texts)
    for i, page in enumerate(pages):
        page.update(img_b64=page_bytes_b64[i], mime=page_mimes[i], para_cards=[])
    for i, p in enumerate(fb.get('paragraph_feedback') or []):
        span, _ = unique_span(full, p.get('original_text', ''))
        targets = [pi for pi in range(count) if span and max(span[0], bounds[pi]) < min(span[1], bounds[pi+1])]
        card = _card_from_para(p, i)
        if not targets:
            card['title'] += '（段落位置待确认）'
        for pi in targets or [0]:
            pages[pi]['para_cards'].append(dict(card))
    return pages, sum(len(p['hotspots']) for p in pages)


# ---------------- 诊断 ----------------
def _diag_show(steps, err=None):
    if not DEBUG:
        return
    with st.expander("🔧 原图批改未启用——诊断信息（内测用，发布前会关闭）", expanded=True):
        for s in steps:
            st.markdown(f"- {s}")
        if err:
            st.code(err)


# ---------------- 主入口 ----------------
def render_image_review(fb, image_bytes, ocr_text, score_text="",
                        essay_id="default", regrade_cb=None,
                        conf_threshold=CONF_THRESHOLD,
                        all_image_bytes=None, ocr_pages=None,
                        ocr_layout_pages=None):
    """成功渲染返回 True；任何失败/降级返回 False（调用方走旧视图）。"""
    steps = []
    try:
        import base64
        import cv2
        import numpy as np
        from image_review_render import build_image_review_html

        imgs = all_image_bytes or ([image_bytes] if image_bytes else [])
        if ocr_pages and len(ocr_pages) == len(imgs):
            texts = ocr_pages
        elif len(imgs) == 1 and ocr_text:
            texts = [ocr_text]
        else:
            texts = None
        steps.append(f"入参：fb={'有' if fb else '空'}，照片 {len(imgs)} 页，"
                     f"分页OCR={'有' if texts else '缺'}")
        if not (fb and imgs and texts):
            _diag_show(steps + ["❌ 入参不齐（纯文字提交无照片属正常；"
                                "多页但 ocr_pages 缺失/页数不符请检查 OCR 缓存）"])
            return False

        locators, b64s, mimes, confs = [], [], [], []
        for bs, txt in zip(imgs, texts):
            im = cv2.imdecode(np.frombuffer(bs, np.uint8), cv2.IMREAD_COLOR)
            locators.append(None)
            b64s.append(base64.b64encode(bs).decode())
            mimes.append("image/jpeg")
            confs.append(round(locators[-1].confidence, 2) if locators[-1] else 0.0)
        steps.append(f"各页对齐置信度 {confs}（阈值 {conf_threshold}，"
                     f"字级圈画={'开' if ENABLE_HOTSPOTS else '关'}）")

        # ── 首选 GLM-OCR 同次响应自带的 layout_details / bbox_2d ──
        layout_locs = None
        layout_ready = [False] * len(imgs)
        try:
            from layout_locator import build_layout_locators
            layout_locs = build_layout_locators(ocr_layout_pages, len(imgs))
            for i, ll in enumerate(layout_locs):
                if ll is None:
                    continue
                # 只有官方坐标对应的 OCR 文字与学生当前核对稿完全一致才使用。
                layout_ready[i] = _norm(texts[i]) == ll.full
                if not layout_ready[i]:
                    layout_locs[i] = None
            steps.append(f"OCR官方坐标:{sum(layout_ready)}/{len(imgs)} 页可用")
        except Exception as _le:
            layout_locs = None
            steps.append(f"OCR官方坐标不可用:{_le}")

        # ── 没有可靠官方坐标的页面，才调用原有逐行视觉定位器 ──
        row_locs = None
        # 2026-08-06 诊断:把逐行后端的成败提到外层,内测诊断行直接可读
        _dx = {"key": False, "ok_pages": 0, "err": ""}
        if ENABLE_HOTSPOTS and HOTSPOT_BACKEND == "row":
            try:
                from row_locator import build_row_locators, img_hash
                _zk = st.secrets.get("ZHIPU_API_KEY", "")
                _zb = st.secrets.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn")
                from annotation_core import build_ledger
                _pre = build_ledger(fb, texts, [[x] for x in (layout_locs or [None]*len(imgs))])
                fallback_indexes = [i for i in range(len(imgs)) if not layout_ready[i]]
                if any(a['status'] == 'unlocated' for a in _pre):
                    fallback_indexes = list(range(len(imgs)))
                fallback_imgs = [imgs[i] for i in fallback_indexes]
                _all_cached = all(("rowloc_" + img_hash(bs)) in st.session_state
                                  for bs in fallback_imgs)
                if _zk:
                    fallback_locs = []
                    if fallback_imgs:
                        if _all_cached:
                            fallback_locs = build_row_locators(
                                fallback_imgs, _zk, _zb, cache=st.session_state)
                        else:
                            with st.spinner("正在核对缺少坐标的文字行，请稍候…"):
                                fallback_locs = build_row_locators(
                                    fallback_imgs, _zk, _zb, cache=st.session_state)
                    row_locs = [None] * len(imgs)
                    for index, locator in zip(fallback_indexes, fallback_locs):
                        row_locs[index] = locator
                _ok_pages = sum(1 for r in (row_locs or []) if r is not None)
                _dx["key"] = bool(_zk)
                _dx["ok_pages"] = _ok_pages
                steps.append(f"逐行定位后端:{_ok_pages}/{len(imgs)} 页转写就绪")
            except Exception as _re:
                row_locs = None
                _dx["err"] = f"{type(_re).__name__}: {_re}"
                steps.append(f"逐行定位后端不可用(不影响批改):{_re}")

        pages, total_hot = _build_pages(fb, locators, b64s, mimes, texts,
                                        row_locs=row_locs, layout_locs=layout_locs)
        steps.append(f"共定位 {total_hot} 处记号，"
                     f"段落卡分派 {[len(p['para_cards']) for p in pages]}")
        if ENABLE_HOTSPOTS and total_hot == 0:
            steps.append("⚠️ 一处记号都没定位到(照片仅原样展示)——"
                         "照片倾斜/横线纸/OCR 与照片差异过大都会导致")

        from annotation_core import source_version, apply_overrides
        from pathlib import Path
        import json
        import hmac
        version = source_version(texts)
        with st.expander("Teacher tools（教师修正）"):
            if not st.session_state.get('annotation_teacher_auth'):
                pw = st.text_input("Teacher password（教师密码）", type="password", key=f"ann_pw_{essay_id}")
                if st.button("Enable editing（开启修正）", key=f"ann_login_{essay_id}"):
                    configured = st.secrets.get('ADMIN_PASSWORD', '')
                    if configured and hmac.compare_digest(pw, configured):
                        st.session_state['annotation_teacher_auth'] = True
                    else:
                        st.error("Teacher password is incorrect or not configured（请核对教师密码配置）。")
            if st.session_state.get('annotation_teacher_auth'):
                st.caption("Select an issue, then draw its box. Save before exporting PDF（选批注、框选位置，保存后再导出）。")
        editable = bool(st.session_state.get('annotation_teacher_auth'))
        audit = fb.get('language_audit')
        if audit:
            completed = sum(j.get('status') == 'complete' for j in audit.get('jobs', []))
            st.caption(f"Language check（语言复核）: {completed}/{len(audit.get('jobs', []))} sections complete. Supplementary findings do not automatically change the grade（补充批注不自动改分）。")
        if audit and not audit.get('complete'):
            if st.button("Retry unfinished checks（补查未完成部分）", key=f"retry_audit_{essay_id}"):
                try:
                    from openai import OpenAI
                    from language_audit import audit_language, openai_call
                    from database import save_language_audit
                    client = OpenAI(api_key=st.secrets['DEEPSEEK_API_KEY'], base_url='https://api.deepseek.com', timeout=90, max_retries=0)
                    with st.spinner("Checking unfinished sections（补查中）…"):
                        retry = audit_language(texts, openai_call(client, st.secrets.get('LANGUAGE_AUDIT_MODEL', 'deepseek-v4-flash')), cache=st.session_state)
                    save_language_audit(int(essay_id), st.session_state.get('student_id'), retry)
                    fb['language_audit'] = retry
                    st.rerun()
                except Exception:
                    st.error("Retry could not be saved（补查或保存失败，请重试）。")
        html = build_image_review_html(pages, _build_top_issue(fb), score_text, editable, version)
        review_component = components.declare_component('annotation_review_v2',
                              path=str(Path(__file__).with_name('review_component')))
        event = review_component(html=html, key=f"review_{essay_id}", default=None)
        last_key = f"annotation_saved_{essay_id}"
        if (editable and isinstance(event, dict) and event.get('event_id')
                and event['event_id'] != st.session_state.get(last_key)):
            if event.get('source_version') != version:
                st.error("Text changed. Reload and position again（原文已变，请重新定位）。")
            else:
                old = fb.get('annotation_overrides') or {}
                merged = {a['id']: a for a in old.get('items', [])} if old.get('source_version') == version else {}
                edits = event.get('items')
                for item in (edits if isinstance(edits, list) else [])[:1000]:
                    if isinstance(item, dict) and isinstance(item.get('id'), str):
                        merged[item['id']] = item
                ledger = [a for p in pages for a in p.get('issues', [])]
                checked = apply_overrides(ledger, dict(source_version=version, items=list(merged.values())), len(imgs), version)
                # Persist only server-validated fields and coordinates.
                saved = dict(source_version=version, items=[dict(id=a['id'], quote=a['quote'],
                         fix=a['fix'], why=a['why'], dismissed=a['status']=='dismissed',
                         locations=a['locations'] if a['status']=='manual' else [])
                         for a in checked if a['id'] in merged])
                try:
                    from database import save_annotation_overrides
                    save_annotation_overrides(int(essay_id), st.session_state.get('student_id'), saved)
                    fb['annotation_overrides'] = saved
                    st.session_state[last_key] = event['event_id']
                    st.session_state[f"annotation_notice_{essay_id}"] = True
                    st.rerun()
                except Exception:
                    st.error("Could not save corrections（保存失败，请重试）；请勿关闭此页。")
        if st.session_state.pop(f"annotation_notice_{essay_id}", False):
            st.success("Corrections saved（修正已保存），PDF will use the same positions（导出同步）。")
        st.caption("All detected findings stay in the list, including those needing position checks（已发现的问题全部保留，待定位不丢失）。")
        _render_ocr_fix(ocr_text, essay_id, regrade_cb, ocr_pages=texts)
        return True

    except Exception:
        _diag_show(steps + ["❌ 未预期异常："], traceback.format_exc())
        return False                     # 新模块任何异常都不许弄崩结果页


def _render_ocr_fix(ocr_text, essay_id, regrade_cb, ocr_pages=None):
    """改回原文(2026-07-12 v2):多页时按页分栏编辑,可精确回填各页 OCR;
    回调收到 list(各页文本)——单页也统一走 list。"""
    with st.expander("🖊 识别有错？在这里改回你的原文"):
        st.caption("图上的批改基于机器识别的文字。哪里认错了字,"
                   "直接改成你写的原文,再点重新批改。每篇作文限重批 1 次。")
        pages = ocr_pages if (ocr_pages and any(p for p in ocr_pages)) else [ocr_text]
        fixed_pages = []
        for i, ptxt in enumerate(pages):
            label = f"第 {i + 1} 页原文" if len(pages) > 1 else "你的作文原文"
            fixed_pages.append(st.text_area(
                label, value=ptxt or '', height=200 if len(pages) > 1 else 240,
                key=f"ocrfix_{essay_id}_p{i}"))
        if st.button("🔁 按我的原文重新批改", key=f"regrade_{essay_id}"):
            if regrade_cb is not None:
                regrade_cb(essay_id, fixed_pages)
                st.rerun()
            else:
                st.session_state[f"ocrfix_saved_{essay_id}"] = "\n".join(fixed_pages)
                st.info("已保存你的修正（重新批改功能待接入）。")


# ═══════════════════════════════════════════════════════════
# 2026-07-12:左图右评 PDF 报告的数据源(方案A:批改当次会话内生成,照片不入库)
# ═══════════════════════════════════════════════════════════
def build_annotated_pages_for_pdf(fb, all_image_bytes, ocr_pages,
                                  conf_threshold=CONF_THRESHOLD,
                                  ocr_layout_pages=None):
    """把批改记号直接画到照片上,返回 PDF 报告需要的每页数据:
        [{'image_jpg': bytes, 'para_cards': [...], 'hotspots': [...]}, ...]
    任何失败返回 None(调用方退回纯文字版报告)。与网页视图同一套
    定位结果与严格闸门——网页上圈哪里,PDF 就圈哪里,不另算一遍。"""
    try:
        import base64
        import cv2
        import numpy as np

        imgs = all_image_bytes or []
        texts = ocr_pages or []
        if not (fb and imgs and texts and len(imgs) == len(texts)):
            return None

        mats, locators, b64s, mimes = [], [], [], []
        for bs, txt in zip(imgs, texts):
            im = cv2.imdecode(np.frombuffer(bs, np.uint8), cv2.IMREAD_COLOR)
            if im is None:
                return None
            mats.append(im)
            locators.append(None)
            b64s.append(base64.b64encode(bs).decode())
            mimes.append("image/jpeg")
        # 2026-07-12(晚) 决策:与网页视图同步——置信度不足/零热点都不再整体放弃,
        # 该画的画(低置信页自动不画),照片+右侧段落卡照常进报告
        # 2026-07-13 全量方案:PDF 与网页共用同一份逐行转写缓存——
        # 网页视图渲染时已转写,这里零额外 API 调用;缓存意外缺失时
        # 现场补转写(有密钥)或不画记号(无密钥),报告照常生成。
        layout_locs = None
        layout_ready = [False] * len(imgs)
        try:
            from layout_locator import build_layout_locators
            layout_locs = build_layout_locators(ocr_layout_pages, len(imgs))
            for i, ll in enumerate(layout_locs):
                if ll is None:
                    continue
                layout_ready[i] = _norm(texts[i]) == ll.full
                if not layout_ready[i]:
                    layout_locs[i] = None
        except Exception:
            layout_locs = None

        row_locs = None
        if ENABLE_HOTSPOTS and HOTSPOT_BACKEND == "row":
            try:
                import streamlit as _st_pdf
                from row_locator import build_row_locators
                _zk = _st_pdf.secrets.get("ZHIPU_API_KEY", "")
                _zb = _st_pdf.secrets.get("ZHIPU_BASE_URL",
                                          "https://open.bigmodel.cn")
                if _zk:
                    from annotation_core import build_ledger
                    _pre = build_ledger(fb, texts, [[x] for x in (layout_locs or [None]*len(imgs))])
                    fallback_indexes = [i for i in range(len(imgs)) if not layout_ready[i]]
                    if any(a['status'] == 'unlocated' for a in _pre):
                        fallback_indexes = list(range(len(imgs)))
                    fallback_locs = build_row_locators(
                        [imgs[i] for i in fallback_indexes], _zk, _zb,
                        cache=_st_pdf.session_state)
                    row_locs = [None] * len(imgs)
                    for index, locator in zip(fallback_indexes, fallback_locs):
                        row_locs[index] = locator
            except Exception:
                row_locs = None
        pages, total_hot = _build_pages(fb, locators, b64s, mimes, texts,
                                        row_locs=row_locs, layout_locs=layout_locs)

        RED, GREEN, WHITE = (54, 40, 199), (64, 142, 46), (255, 255, 255)
        out = []
        for pi, page in enumerate(pages):
            im = mats[pi].copy()
            H, W = im.shape[:2]
            th = max(2, W // 450)                      # 线宽随分辨率
            for h in page['hotspots']:
                color = (20, 150, 200) if h.get('mark') == 'region' else (GREEN if h.get('good') else RED)
                mark = h.get('mark')
                for x, y, w, hh in h['rects']:
                    x0, y0 = int(x / 100 * W), int(y / 100 * H)
                    x1, y1 = int((x + w) / 100 * W), int((y + hh) / 100 * H)
                    if mark == 'region':
                        cv2.rectangle(im, (x0, y0), (x1, y1), color, th)
                    elif mark == 'cross':
                        cv2.line(im, (x0, y0), (x1, y1), color, th + 1)
                        cv2.line(im, (x0, y1), (x1, y0), color, th + 1)
                    elif mark == 'circle':
                        cv2.ellipse(im, ((x0 + x1) // 2, (y0 + y1) // 2),
                                    (max((x1 - x0) // 2 + th * 2, 6),
                                     max((y1 - y0) // 2 + th * 2, 6)),
                                    0, 0, 360, color, th)
                    else:                              # line / wavy → 底部划线
                        cv2.line(im, (x0, y1 + th), (x1, y1 + th), color, th + 1)
                # 序号徽章画在首个矩形右上角
                fx, fy, fw, _fh = h['rects'][0]
                bx = int((fx + fw) / 100 * W) + th * 4
                by = int(fy / 100 * H)
                r = max(11, W // 90)
                bx, by = min(bx, W - r - 2), max(by, r + 2)
                cv2.circle(im, (bx, by), r, color, -1)
                cv2.putText(im, str(h['n']), (bx - r // 2 - (2 if h['n'] >= 10 else 0),
                            by + r // 2), cv2.FONT_HERSHEY_SIMPLEX,
                            r / 18.0, WHITE, max(1, th - 1), cv2.LINE_AA)
            ok, buf = cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if not ok:
                return None
            out.append({'image_jpg': buf.tobytes(),
                        'para_cards': page['para_cards'],
                        'hotspots': page['hotspots'], 'issues': page['issues']})
        return out
    except Exception:
        return None

