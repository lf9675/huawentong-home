import streamlit as st
from openai import OpenAI
import urllib.request
import urllib.error
import base64
import json
import sys
import os
import PIL.Image
import io
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_input import normalize_image, layout_envelope, sync_corrected_pages
from database import (get_active_assignments, save_submission, mark_viewed,
                      get_progress_card_data, render_progress_card_html,
                      save_assignment, toggle_assignment, get_all_assignments)
from prompts import (build_grading_prompt, build_user_message, EXAM_LEVELS,
                     finalize_grade_fields)
from access_codes import (init_access_tables, validate_code, check_can_submit,
                          record_usage, get_code_info, nickname_candidates,
                          set_nickname, DAILY_LIMIT, today_usage, save_student_prompt)

st.set_page_config(page_title="学生作文提交", page_icon="✏️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500&display=swap');
* { font-family: 'Noto Sans SC', sans-serif; }
h1,h2,h3 { font-family: 'Noto Serif SC', serif; }
.main { background: #faf8f5; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
section[data-testid="stSidebarUserContent"] { display: none; }
.block-container { padding-top: 3.5rem; padding-bottom: 2rem; }
header[data-testid="stHeader"] { background: transparent; }
.stApp > header { background: transparent; }

.page-header {
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    color: white; border-radius: 16px; padding: 1.5rem 2rem;
    margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem;
}
.page-header h2 { color: #f0c27f; margin: 0; font-size: 1.6rem; }
.page-header p { color: #b8c5d6; margin: 0; font-size: 0.95rem; }

.card {
    background: white; border-radius: 16px; padding: 1.5rem;
    border: 1px solid #e8e0d5; margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.step-badge {
    background: #0f3460; color: #f0c27f; border-radius: 50%;
    width: 28px; height: 28px; display: inline-flex;
    align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem; margin-right: 0.5rem;
}
.assignment-badge {
    background: #f0c27f22; border: 1px solid #f0c27f;
    border-radius: 8px; padding: 0.8rem 1rem;
    color: #7a5c1e; font-size: 0.95rem; margin-bottom: 0.5rem;
}
.ocr-warning {
    background: #fff8e1; border: 1px solid #ffc107;
    border-radius: 8px; padding: 0.8rem 1rem; color: #7a5000;
    font-size: 0.9rem; margin-bottom: 0.8rem;
}
.feedback-section { border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; }
.strengths { background: #e8f5e9; border-left: 4px solid #43a047; }
.issues-lang { background: #fff3e0; border-left: 4px solid #fb8c00; }
.issues-struct { background: #e3f2fd; border-left: 4px solid #1e88e5; }
.issues-content { background: #fce4ec; border-left: 4px solid #e53935; }
.suggestions { background: #f3e5f5; border-left: 4px solid #8e24aa; }
.upgrade-section { background: #f9fbe7; border-left: 4px solid #c0ca33; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; }
.issue-item {
    background: white; border-radius: 8px; padding: 0.8rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.location-tag {
    background: #1a1a2e; color: white; border-radius: 4px;
    padding: 0.1rem 0.5rem; font-size: 0.78rem; margin-right: 0.5rem;
}
.original { color: #c62828; text-decoration: line-through; }
.improved { color: #2e7d32; font-weight: 500; }
.level-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; margin-top: 0.5rem; }
.level-table th { background: #1a1a2e; color: #f0c27f; padding: 0.5rem 0.7rem; text-align: left; font-size: 0.82rem; }
.level-table td { padding: 0.5rem 0.7rem; border-bottom: 1px solid #e8e0d5; vertical-align: top; }
.level-table tr:nth-child(even) td { background: #fafaf0; }
.orig-cell { color: #c62828; }
.mid-cell { color: #e65100; }
.best-cell { color: #2e7d32; font-weight: 500; }
.tip-cell { color: #6a1b9a; font-size: 0.78rem; background: #f3e5f5; border-radius: 4px; padding: 0.2rem 0.4rem; }
.stButton > button {
    background: linear-gradient(135deg, #0f3460, #16213e);
    color: white; border: none; border-radius: 10px;
    padding: 0.7rem 2rem; font-family: 'Noto Sans SC', sans-serif;
    font-size: 1rem; font-weight: 500; width: 100%;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(15,52,96,0.3); }
.stTextInput > div > div > input { border-radius: 10px; border-color: #e8e0d5; }
</style>
""", unsafe_allow_html=True)

# ── 顶部导航栏 ───────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);border-radius:12px;
    padding:0.9rem 1.5rem;margin-bottom:1rem;display:flex;justify-content:space-between;
    align-items:center;flex-wrap:wrap;gap:1rem;box-shadow:0 4px 16px rgba(0,0,0,0.08);">
    <div>
        <span style="color:#f0c27f;font-family:'Noto Serif SC',serif;font-size:1.15rem;font-weight:700;">
            CLever · 华文通
        </span>
        <span style="color:#b8c5d6;font-size:0.8rem;margin-left:0.5rem;">
            学生作文提交
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 横向导航按钮 ──
st.markdown("""<style>
.nav-row .stButton > button {
    background: transparent; color: #1a1a2e; border: 1px solid #e8e0d5;
    border-radius: 8px; padding: 0.4rem 1rem; font-size: 0.9rem;
    font-weight: 500; width: 100%; height: 40px; transition: all 0.2s;
}
.nav-row .stButton > button:hover {
    background: #fdf8ee; border-color: #f0c27f; color: #7a5c1e;
    transform: none; box-shadow: none;
}
</style><div class="nav-row">""", unsafe_allow_html=True)
nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    if st.button("🏠 首页", key="nav_home_s"):
        st.switch_page("app.py")
with nav2:
    st.button("🎓 学生作文提交", key="nav_student_s", disabled=True)
with nav3:
    if st.button("👩‍🏫 教师管理后台", key="nav_admin_s"):
        st.switch_page("pages/admin.py")
with nav4:
    if st.button("📈 学生进步追踪", key="nav_progress_s"):
        st.switch_page("pages/progress.py")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

assignments = get_active_assignments()  # 老师布置的题目(可选,可以为空)

# ── 实用文支持(2026-07-06 决策)─────────────────────────────
# 文体由学生自选;选中实用文文体后,考试段自动切换到对应的 PRACTICAL 档位
# (访问码本身仍只按 HCL/O_CL/N_CL 发放,不需要单独发实用文码)
PRACTICAL_GENRES = ("私人电邮", "公务电邮", "网上论坛")
PRACTICAL_LEVEL_MAP = {"HCL": "PRACTICAL_HCL", "O_CL": "PRACTICAL_O", "N_CL": "PRACTICAL_N"}


def effective_exam_level(code_level, genre):
    """实用文文体 → 对应实用文档位;作文文体 → 原考试段"""
    if genre in PRACTICAL_GENRES:
        return PRACTICAL_LEVEL_MAP.get(code_level, "PRACTICAL_HCL")
    return code_level


def get_or_create_self_assignment(exam_level, genre):
    """自带题目的占位作业(is_active=0,学生选不到,老师后台提交列表能看到)。
    每个 考试段×文体 一条,避免 get_all_submissions 的 INNER JOIN 吞掉提交。"""
    title = f"学生自带题目·{genre}"
    for a in get_all_assignments():
        if a.get('title') == title and a.get('exam_level') == exam_level:
            return a['id']
    aid = save_assignment(title, exam_level, genre,
                          "(题目由学生提交时提供,见批改记录)", "", "", [])
    toggle_assignment(aid, 0)
    return aid


def glm_ocr_prompt_photo(img_bytes, media_type="image/jpeg"):
    """识别题目照片(单张,小图)。与作文 OCR 走同一 GLM-OCR 接口。"""
    ZHIPU_API_KEY = st.secrets["ZHIPU_API_KEY"]
    url = "https://open.bigmodel.cn/api/paas/v4/layout_parsing"
    # 超大图先压一道
    if len(img_bytes) > 3_000_000:
        im = PIL.Image.open(io.BytesIO(img_bytes)).convert("RGB")
        im.thumbnail((2000, 2000))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=85)
        img_bytes, media_type = buf.getvalue(), "image/jpeg"
    b64 = base64.standard_b64encode(img_bytes).decode()
    payload = json.dumps({"model": "glm-ocr",
                          "file": f"data:{media_type};base64,{b64}"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST",
                                 headers={"Authorization": f"Bearer {ZHIPU_API_KEY}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    md = result.get("md_results", "")
    txt = re.sub(r'[#*>`|]|<[^>]+>', '', md)
    return " ".join(txt.split())

# ═══════════════════════════════════════════════════════════
# STAGE 0 — 访问码验证(一码通:码即身份+密码,零 PII)
# ═══════════════════════════════════════════════════════════
init_access_tables()

if 'code_info' not in st.session_state:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="step-badge">🔑</span> **输入访问码**', unsafe_allow_html=True)
    st.caption("访问码由老师发放,例如 HW-K7M3-P9Q2。大小写不限,记得输入横线。")
    code_input = st.text_input("访问码", placeholder="HW-XXXX-XXXX",
                               label_visibility="collapsed", key="code_input_box")
    if st.button("进入", type="primary", key="code_enter"):
        ok, info, reason = validate_code(code_input)
        if not ok:
            st.error(reason)
        else:
            st.session_state['pending_code_info'] = info
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 首次使用:挑选昵称(系统生成,只能选不能填)──────────
    if 'pending_code_info' in st.session_state:
        pinfo = st.session_state['pending_code_info']
        if pinfo.get('nickname'):
            st.session_state['code_info'] = pinfo
            st.session_state.pop('pending_code_info', None)
            st.rerun()
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**🎨 第一次使用,先挑一个昵称吧!**")
            st.caption("为了保护你的隐私,这里不填真实姓名。从下面挑一个喜欢的,以后批改结果都用它称呼你。")
            if 'nick_options' not in st.session_state:
                st.session_state['nick_options'] = nickname_candidates(6)
            chosen = st.radio("挑一个:", st.session_state['nick_options'],
                              horizontal=True, key="nick_radio")
            nc1, nc2 = st.columns(2)
            with nc1:
                if st.button("🔄 换一批", key="nick_refresh"):
                    st.session_state['nick_options'] = nickname_candidates(6)
                    st.rerun()
            with nc2:
                if st.button("✅ 就用这个!", type="primary", key="nick_confirm"):
                    set_nickname(pinfo['id'], chosen)
                    st.session_state['code_info'] = get_code_info(pinfo['id'])
                    st.session_state.pop('pending_code_info', None)
                    st.session_state.pop('nick_options', None)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 已验证:取当前额度状态(每次刷新都查库,保证显示准确)
code_info = get_code_info(st.session_state['code_info']['id'])
if code_info is None or not code_info['is_active']:
    st.error("访问码已失效,请联系老师。")
    st.session_state.pop('code_info', None)
    st.stop()
st.session_state['code_info'] = code_info
_today_used = today_usage(code_info['id'])

# ── 欢迎条:昵称 + 用量可见(学生自己就是泄露探测器)──────
w1, w2 = st.columns([5, 1])
with w1:
    st.markdown(
        f"👋 你好,**{code_info['nickname']}**!"
        + (f"　新作文:**{code_info.get('new_essays_used') or 0}/{code_info['new_essays_total']}** 篇"
           f"　·　总次数(含重交):**{code_info['essays_used']}/{code_info['essays_total']}**"
           if (code_info.get('new_essays_total') or 0) > 0 else
           f"　批改额度:已用 **{code_info['essays_used']}/{code_info['essays_total']}** 篇")
        + f"　·　今天还可提交 **{max(DAILY_LIMIT - _today_used, 0)}** 篇"
        + f"　·　有效期至 {code_info['expiry']}"
    )
with w2:
    if st.button("退出", key="code_logout", use_container_width=True):
        for k in ['code_info', 'pending_code_info', 'nick_options',
                  'feedback', 'sub_id', 'ocr_done', 'ocr_text', 'ocr_pages',
                  'ocr_layout_pages', 'image_bytes', 'all_image_bytes']:
            st.session_state.pop(k, None)
        st.rerun()

# ═══════════════════════════════════════════════════════════
# STAGE 1 — Student info + upload
# ═══════════════════════════════════════════════════════════
if 'ocr_done' not in st.session_state:
    st.session_state['ocr_done'] = False
if 'feedback' not in st.session_state:
    st.session_state['feedback'] = None

if not st.session_state['ocr_done']:

    # ══════════════════════════════════════════════════════════
    # 模块 0.5:我的批改记录(2026-07-05 决策)
    # 修复:退出登录后 session 清空,旧报告没有入口找回。
    # 从库里按访问码重现完整报告;查看历史为只读,不消耗每日额度。
    # ══════════════════════════════════════════════════════════
    try:
        from database import get_student_history, get_submission_for_student
        _hist_sid = f"AC{code_info['id']}"
        _history = get_student_history(_hist_sid)
    except Exception:
        _history = []
    if _history:
        with st.expander(f"📂 我的批改记录（{len(_history)} 篇）— 点开可重看以前的批改报告",
                         expanded=False):
            for _rec in _history:
                _date = str(_rec.get('submitted_at') or '')[:16].replace('T', ' ')
                _score = _rec.get('display_total')
                _grade = _rec.get('grade') or ''
                _title = _rec.get('title') or ''
                _genre = _rec.get('genre') or ''
                _score_txt = f"{_score} 分 · {_grade}" if _score is not None else ''
                _rc1, _rc2 = st.columns([5, 1])
                with _rc1:
                    st.markdown(
                        f"<div style='padding:0.35rem 0;font-size:0.88rem;color:#2c2c2a;'>"
                        f"<strong>{_date}</strong>　{_genre}　{_title}　"
                        f"<span style='color:#7a5c1e;'>{_score_txt}</span></div>",
                        unsafe_allow_html=True)
                with _rc2:
                    if st.button("查看", key=f"hist_view_{_rec['id']}",
                                 use_container_width=True):
                        try:
                            _loaded = get_submission_for_student(_rec['id'], _hist_sid)
                        except Exception:
                            _loaded = None
                        if _loaded is None:
                            st.error("这份报告读取失败,请稍后再试。")
                        else:
                            # 清掉上一份报告的控件残留,避免版本选择串台
                            for _k in [k for k in st.session_state.keys()
                                       if str(k).startswith('para_ver_')]:
                                st.session_state.pop(_k, None)
                            st.session_state.pop('model_essay_ver', None)
                            st.session_state['feedback'] = _loaded['feedback']
                            st.session_state['sub_id'] = _rec['id']
                            st.session_state['parent_submission_id'] = _loaded.get('parent_submission_id')
                            st.session_state['student_id'] = _hist_sid
                            st.session_state['student_name'] = code_info.get('nickname', '同学')
                            st.session_state.setdefault('tts_lang', '普通话 (Mandarin)')
                            st.session_state['selected_assignment'] = {
                                'title': _loaded['title'],
                                'genre': _loaded['genre'],
                                'prompt': _loaded['prompt'],
                                'exam_level': (_loaded['exam_level']
                                               or code_info.get('exam_level', 'HCL')),
                            }
                            st.session_state['ocr_done'] = True
                            st.rerun()

    # ══════════════════════════════════════════════════════════
    # 模块 0.6:提交类型申报(2026-07-05 双轨额度)
    # 新作文占"新作文额度";修改后重交只占总次数 — 鼓励改了再交的学习循环。
    # 申报制 + 提交时相似度兜底(见批改按钮处),不靠 AI 自动判定。
    # ══════════════════════════════════════════════════════════
    st.session_state['parent_submission_id'] = None
    _dual_track = (code_info.get('new_essays_total') or 0) > 0
    if _dual_track and _history:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _kind = st.radio(
            "这次要批改的是?",
            ["📝 一篇新作文", "🔁 之前批改过、修改后重交(不占新作文额度)"],
            horizontal=True, key="submit_kind_radio")
        if "重交" in _kind:
            _fmt_hist = lambda r: (f"{str(r.get('submitted_at') or '')[:10]} · "
                                   f"{r.get('genre') or ''} · {(r.get('title') or '')[:15]} · "
                                   f"{r.get('display_total') or '?'} 分")
            _parent_rec = st.selectbox("是哪一篇的修改版?", _history,
                                       format_func=_fmt_hist, key="parent_pick")
            st.session_state['parent_submission_id'] = _parent_rec['id']
            st.caption("批改后会自动和上一版对比,让你看到分数变化。")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="step-badge">1</span> **作文题目**', unsafe_allow_html=True)
    st.caption("🔒 隐私提醒:作文里不要写自己的真实姓名和学校名字哦。")

    src_options = ["✍️ 输入题目文字", "📷 拍题目照片", "🤷 我没有题目"]
    if assignments:
        src_options.append("👩‍🏫 老师布置的题目")
    prompt_source = st.radio("题目从哪里来?", src_options, horizontal=True)

    selected_assignment = None
    prompt_text, requirements = "", ""
    no_prompt_mode = False
    code_exam_level = code_info.get('exam_level') or 'HCL'

    if "老师布置" in prompt_source:
        assignment_options = {f"{a['title']} ({a['genre']})": a for a in assignments}
        selected_label = st.selectbox("选择作文题目", list(assignment_options.keys()))
        selected_assignment = assignment_options[selected_label]
        genre = selected_assignment['genre']
        st.markdown(f'<div class="assignment-badge">📌 <strong>题目：</strong>{selected_assignment["prompt"]}</div>', unsafe_allow_html=True)
        if selected_assignment.get('requirements'):
            st.markdown(f'<div class="assignment-badge" style="background:#e3f2fd22;border-color:#1e88e5;color:#1a3a5c;">📋 <strong>写作要求：</strong>{selected_assignment["requirements"]}</div>', unsafe_allow_html=True)
    else:
        # 2026-07-06: 文体选项 = 该考试段作文文体 + 实用文文体(私人电邮/公务电邮/网上论坛)
        _prac_key = PRACTICAL_LEVEL_MAP.get(code_exam_level, 'PRACTICAL_HCL')
        genre_options = (EXAM_LEVELS.get(code_exam_level, EXAM_LEVELS['HCL'])['genres']
                         + EXAM_LEVELS[_prac_key]['genres'])
        genre = st.selectbox("这是什么文体?", genre_options)
        if genre in PRACTICAL_GENRES:
            _prac_cfg = EXAM_LEVELS[_prac_key]
            st.caption(f"📋 实用文按 {_prac_cfg['essay_total']} 分制批改"
                       f"(内容 {_prac_cfg['content_max']} + 语文与结构 {_prac_cfg['language_max']}),"
                       f"字数 {_prac_cfg['min_words']} 字以上。"
                       f"记得把题目里的来邮内容或网民贴文一起拍进题目照片/抄进题目栏,批改才准。")

        if "输入题目" in prompt_source:
            prompt_text = st.text_input("题目", placeholder="把作文题目抄在这里")
            requirements = st.text_area("写作要求(可选,题目下面的小字说明)", height=68)
        elif "拍题目" in prompt_source:
            pf = st.file_uploader("上传题目照片(一张)", type=["jpg", "jpeg", "png"],
                                  accept_multiple_files=False, key="prompt_photo")
            if pf and st.button("🔍 识别题目文字", key="btn_ocr_prompt"):
                try:
                    with st.spinner("正在识别题目……"):
                        mt = "image/png" if pf.name.lower().endswith("png") else "image/jpeg"
                        st.session_state['prompt_ocr'] = glm_ocr_prompt_photo(pf.read(), mt)
                except Exception as e:
                    st.error(f"题目识别出错:{e},可以改用手动输入。")
            prompt_text = st.text_input("题目(识别结果,可直接修改)",
                                        value=st.session_state.get('prompt_ocr', ''))
            requirements = st.text_area("写作要求(可选)", height=68, key="req_photo")
        else:
            no_prompt_mode = True
            st.info("没关系!AI 会从你的作文内容猜出题目和主题来批改。"
                    "不过要注意:'切不切题'这部分是估算的,下次带上题目,批改会更准哦。")
            if genre in PRACTICAL_GENRES:
                st.warning("⚠️ 实用文强烈建议提供题目:电邮批改要对照来邮的问题,"
                           "论坛批改要核对你有没有回应每一位网民。没有题目时,"
                           "这两项只能按你的作文内容估算,分数会不太准。")

    school_score = st.text_input(
        "学校老师给的分数(可选)",
        placeholder="如果这篇作文老师已经打过分,填在这里(如 35),帮助系统越改越准",
        key="school_score_input")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 输入方式选择 ─────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="step-badge">2</span> **选择输入方式**', unsafe_allow_html=True)
    input_method = st.radio(
        "请选择：",
        ["📷 方式一：上传照片，系统自动识别（推荐）", "✍️ 方式二：自己输入或粘贴文字"],
        horizontal=False
    )
    st.markdown('</div>', unsafe_allow_html=True)

    uploaded_files = []
    manual_text = ""

    if "方式一" in input_method:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📷 上传作文照片（可多张）**")
        st.caption("作文有几页就上传几张，系统会用AI识别文字，识别后可手动修改。")
        uploaded_files = st.file_uploader(
            "请上传作文照片（JPG / PNG，可同时选多张）",
            type=["jpg","jpeg","png"],
            accept_multiple_files=True
        )
        if uploaded_files:
            st.caption(f"已上传 {len(uploaded_files)} 张照片：")
            cols = st.columns(min(len(uploaded_files), 3))
            for i, f in enumerate(uploaded_files):
                with cols[i % 3]:
                    st.image(f, caption=f"第{i+1}页", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**✍️ 输入或粘贴作文文字**")
        manual_text = st.text_area(
            "在这里输入或粘贴你的作文：",
            placeholder="请在这里输入你的作文全文……",
            height=400,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="step-badge">3</span> **选择语音反馈语言**', unsafe_allow_html=True)
    tts_lang = st.radio("批改结果将以你选择的语言朗读", ["普通话 (Mandarin)", "英语 (English)"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    _can, _why = check_can_submit(code_info['id'],
        is_new_essay=(st.session_state.get('parent_submission_id') is None))
    _need_prompt = ("输入题目" in prompt_source or "拍题目" in prompt_source)
    _prompt_ok = bool(prompt_text.strip()) if _need_prompt else True

    if "方式一" in input_method:
        can_submit = bool(uploaded_files) and _can and _prompt_ok
        if not _can:
            st.warning(_why)
        elif not _prompt_ok:
            st.warning("请先填好(或识别出)作文题目。实在没有题目,可以选'我没有题目'。")
        elif not uploaded_files:
            st.warning("请上传作文照片。")
    else:
        can_submit = bool(manual_text.strip()) and _can and _prompt_ok
        if not _can:
            st.warning(_why)
        elif not _prompt_ok:
            st.warning("请先填好(或识别出)作文题目。实在没有题目,可以选'我没有题目'。")
        elif not manual_text.strip():
            st.warning("请输入作文内容。")

    # ── 统一构建本次提交的"作业"对象 ─────────────────────────
    if selected_assignment is None:
        no_prompt_rubric = ""
        if no_prompt_mode:
            no_prompt_rubric = (
                "学生没有提供作文题目。请先从作文内容反推最可能的题目或主题,"
                "在总评开头用一句话告诉学生你推断的主题是什么;"
                "'切合题意'相关判断按反推主题估算,并在 grade_distance 里提醒学生:"
                "下次提供真实题目,审题和内容分析会更准确。")
        _eff_level = effective_exam_level(code_exam_level, genre)  # 2026-07-06: 实用文自动切档
        submit_asgn = {
            'id': get_or_create_self_assignment(_eff_level, genre),
            'title': f"学生自带题目·{genre}",
            'genre': genre,
            'prompt': prompt_text.strip() if prompt_text.strip() else "(学生未提供题目)",
            'requirements': requirements.strip(),
            'exam_level': _eff_level,
            'rubric': no_prompt_rubric,
            'focus_areas': '[]',
        }
    else:
        submit_asgn = selected_assignment
    prompt_meta = {
        'source': prompt_source,
        'prompt_text': prompt_text.strip(),
        'requirements': requirements.strip(),
        'genre': genre,
        'school_score': school_score.strip(),
    }

    if "方式二" in input_method:
        if st.button("🚀 直接提交批改！", disabled=not can_submit):
            st.session_state['ocr_text'] = manual_text.strip()
            st.session_state['ocr_pages'] = []
            st.session_state['ocr_layout_pages'] = []
            st.session_state['image_bytes'] = b''
            st.session_state['all_image_bytes'] = []
            st.session_state['all_image_names'] = []
            st.session_state['selected_assignment'] = submit_asgn
            st.session_state['prompt_meta'] = prompt_meta
            st.session_state['student_id'] = f"AC{code_info['id']}"
            st.session_state['student_name'] = code_info['nickname']
            st.session_state['tts_lang'] = tts_lang
            st.session_state['ocr_done'] = True
            st.rerun()

    _rotations = []
    if "方式一" in input_method and uploaded_files:
        with st.expander("Check page direction（核对页面方向）", expanded=True):
            st.caption("Rotate until handwriting is upright（把文字转正，再识别）。")
            for _i, _file in enumerate(uploaded_files):
                _angle = st.selectbox(f"Page {_i+1}（第{_i+1}页）", [0, 90, 180, 270],
                                     format_func=lambda v: f"Clockwise {v}°（顺时针）",
                                     key=f"rotation_{_i}_{_file.name}_{_file.size}")
                _rotations.append(_angle)
                try:
                    _preview = PIL.Image.open(io.BytesIO(normalize_image(_file.getvalue(), _angle)))
                    st.image(_preview, width=260)
                except Exception:
                    st.warning(f"第 {_i+1} 页图片无法读取，请重新上传。")

    if "方式一" in input_method and st.button("📷 识别作文文字（核对后才批改）", disabled=not can_submit):
        with st.spinner(f"正在识别 {len(uploaded_files)} 张照片的文字，请稍候……"):
            try:
                # Read all images
                all_image_bytes = [normalize_image(f.getvalue(), _rotations[i]) for i, f in enumerate(uploaded_files)]

                # ── OCR 用智谱 GLM-OCR ────────────────────────────────
                # DeepSeek V4 是纯文本模型，看不了图；「识别图片」这一步用智谱 GLM-OCR
                # （手写体专项优化，0.2元/百万tokens，一篇作文成本可忽略），
                # 批改主体仍走 DeepSeek（见下方）。
                # Secrets 需配置 ZHIPU_API_KEY；
                # 默认走国内 bigmodel.cn，若在国际版 z.ai 注册，
                # 在 Secrets 里加 ZHIPU_BASE_URL = "https://api.z.ai" 即可。
                ZHIPU_API_KEY = st.secrets["ZHIPU_API_KEY"]
                ZHIPU_BASE = st.secrets.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn").rstrip("/")
                OCR_URL = f"{ZHIPU_BASE}/api/paas/v4/layout_parsing"
                OCR_MAX_BYTES = 9 * 1024 * 1024  # 接口单图上限10MB，留1MB余量

                def get_media_type(filename):
                    ext = filename.split(".")[-1].lower()
                    return "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"

                def shrink_if_needed(img_bytes):
                    """照片超过接口大小限制时自动压缩为JPEG，学生无感知。"""
                    if len(img_bytes) <= OCR_MAX_BYTES:
                        return img_bytes, None
                    img = PIL.Image.open(io.BytesIO(img_bytes))
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    for quality in (85, 70, 55):
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=quality)
                        if buf.tell() <= OCR_MAX_BYTES:
                            return buf.getvalue(), "image/jpeg"
                    # 仍超限则减半分辨率后再存
                    img = img.resize((img.width // 2, img.height // 2))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=70)
                    return buf.getvalue(), "image/jpeg"

                def clean_ocr_markdown(md_text):
                    """GLM-OCR 返回 Markdown 格式，去掉排版符号，还原成纯作文文字。"""
                    lines = []
                    for line in md_text.splitlines():
                        s = line.strip()
                        s = re.sub(r'^#{1,6}\s*', '', s)          # 标题符号
                        s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)    # 加粗
                        s = re.sub(r'\*(.*?)\*', r'\1', s)        # 斜体
                        s = re.sub(r'^[-*>]\s+', '', s)           # 列表/引用符号
                        s = re.sub(r'<[^>]+>', '', s)             # HTML 标签
                        if s:
                            lines.append(s)
                    return "\n".join(lines)

                def ocr_one_image(img_bytes, filename):
                    body, forced_mt = shrink_if_needed(img_bytes)
                    mt = "image/jpeg"  # normalize_image already made the canonical JPEG
                    b64 = base64.standard_b64encode(body).decode()
                    payload = json.dumps({
                        "model": "glm-ocr",
                        "file": f"data:{mt};base64,{b64}",
                    }).encode("utf-8")
                    req = urllib.request.Request(
                        OCR_URL,
                        data=payload,
                        headers={
                            "Authorization": f"Bearer {ZHIPU_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        result = json.loads(resp.read().decode("utf-8"))
                    md = result.get("md_results", "")
                    if not md:
                        raise RuntimeError(f"GLM-OCR 未返回识别文字：{str(result)[:200]}")
                    # 同时保留 GLM-OCR 官方 layout_details/bbox_2d，供原图圈注直接定位。
                    return clean_ocr_markdown(md), layout_envelope(result)

                all_pages, all_layout_pages = [], []
                for i, (img_bytes, img_file) in enumerate(zip(all_image_bytes, uploaded_files)):
                    try:
                        page_text, page_layout = ocr_one_image(img_bytes, img_file.name)
                        all_pages.append(page_text)
                        all_layout_pages.append(page_layout)
                    except urllib.error.HTTPError as he:
                        err_body = he.read().decode("utf-8", errors="replace")[:200] if he.fp else str(he)
                        raise RuntimeError(f"第{i+1}页识别失败（HTTP {he.code}）：{err_body}")
                ocr_text = "\n".join(all_pages)

                st.session_state['ocr_text'] = ocr_text
                st.session_state['ocr_pages'] = all_pages   # 2026-07-08 各页OCR分开存,供多页原图批改分页定位
                st.session_state['ocr_layout_pages'] = all_layout_pages
                st.session_state['image_bytes'] = all_image_bytes[0]
                st.session_state['all_image_bytes'] = all_image_bytes
                st.session_state['all_image_names'] = [f.name for f in uploaded_files]
                st.session_state['selected_assignment'] = submit_asgn
                st.session_state['prompt_meta'] = prompt_meta
                st.session_state['student_id'] = f"AC{code_info['id']}"
                st.session_state['student_name'] = code_info['nickname']
                st.session_state['tts_lang'] = tts_lang
                st.session_state['ocr_done'] = True
                st.rerun()

            except Exception as e:
                st.error(f"识别出错：{e}")

# ═══════════════════════════════════════════════════════════
# STAGE 2 — OCR verification
# ═══════════════════════════════════════════════════════════
elif st.session_state['ocr_done'] and not st.session_state['feedback']:

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="step-badge">4</span> **核对识别文字**', unsafe_allow_html=True)
    st.markdown('<div class="ocr-warning">⚠️ 请仔细核对下面识别出来的文字，如有错误请直接修改，然后再点击"提交批改"。这也是你重新检查自己作文的好机会！</div>', unsafe_allow_html=True)

    col_orig, col_ocr = st.columns(2)
    with col_orig:
        all_imgs = st.session_state.get('all_image_bytes', [st.session_state['image_bytes']])
        st.markdown(f"**📸 原图（共{len(all_imgs)}页）**")
        for i, img_b in enumerate(all_imgs):
            st.image(img_b, caption=f"第{i+1}页", use_container_width=True)
    with col_ocr:
        st.markdown("**📝 识别出的文字（可直接修改）**")
        st.caption("如识别不准确，可借助其他工具识别后粘贴到这里，再点提交。")
        _source_pages = st.session_state.get('ocr_pages') or [st.session_state['ocr_text']]
        _corrected_pages = []
        for _i, _page in enumerate(_source_pages):
            _corrected_pages.append(st.text_area(
                label=f"Page {_i+1} text（第{_i+1}页原文）", value=_page,
                height=350, key=f"verify_page_{_i}_" + __import__('hashlib').sha256(_page.encode()).hexdigest()[:12]))
        corrected_text = "\n".join(_corrected_pages)
    st.markdown('</div>', unsafe_allow_html=True)

    col_back, col_submit = st.columns(2)
    with col_back:
        if st.button("← 重新上传"):
            st.session_state['ocr_done'] = False
            st.rerun()
    with col_submit:
        # 2026-07-12:重批回调置 regrade_autorun 后落回本 Stage,自动触发提交,
        # 文本框此时已显示学生改正后的原文,corrected_text 自然取到新值
        if st.button("🚀 确认无误，提交批改！") or st.session_state.pop('regrade_autorun', False):
            corrected_text = sync_corrected_pages(st.session_state, _corrected_pages)
            _parent_sid = st.session_state.get('parent_submission_id')
            # ── 相似度兜底(2026-07-05):申报了重交但文本和原作差异过大 → 按新作文计 ──
            if _parent_sid:
                try:
                    from database import get_submission_brief
                    import difflib as _difflib
                    _pb = get_submission_brief(_parent_sid, st.session_state['student_id'])
                    _ratio = (_difflib.SequenceMatcher(
                        None, (_pb or {}).get('ocr_text') or '', corrected_text).ratio()
                        if _pb else 0)
                    if _ratio < 0.30:
                        _parent_sid = None
                        st.session_state['parent_submission_id'] = None
                        st.info("这篇和你选的原作差别很大,系统按【新作文】为你批改和计额度。")
                except Exception:
                    pass  # 兜底比对失败不拦路,按学生申报处理
            _ok, _reason = check_can_submit(st.session_state['code_info']['id'],
                                            is_new_essay=(_parent_sid is None))
            if not _ok:
                st.error(_reason)
                st.stop()
            with st.spinner("AI 正在仔细批改你的作文，请稍候约30秒……"):
                try:
                    client = OpenAI(
                        api_key=st.secrets["DEEPSEEK_API_KEY"],
                        base_url="https://api.deepseek.com",
                    )
                    asgn = st.session_state['selected_assignment']
                    genre = asgn['genre']
                    rubric = asgn.get('rubric', '')
                    prompt_text = asgn['prompt']
                    requirements = asgn.get('requirements', '')
                    exam_level = asgn.get('exam_level', 'HCL')  # 默认 HCL，向后兼容旧数据

                    try:
                        focus_list = json.loads(asgn.get('focus_areas') or '[]')
                    except:
                        focus_list = []

                    # ── 用新的 SEAB 标准 prompt 引擎 ──────────────
                    # 2026-07-05:拍照提交传 is_handwritten,批改时启用 OCR 宽容规则
                    system_prompt = build_grading_prompt(
                        exam_level=exam_level,
                        genre=genre,
                        prompt_text=prompt_text,
                        requirements=requirements,
                        focus_areas=focus_list,
                        custom_rubric=rubric if rubric else None,
                        is_handwritten=bool(st.session_state.get('image_bytes')),
                    )

                    user_msg = build_user_message(
                        prompt_text=prompt_text,
                        requirements=requirements,
                        genre=genre,
                        essay_text=corrected_text,
                    )

                    # ── API调用：用 streaming 模式避免长输出超时 ───────────
                    with st.spinner("AI 正在批改你的作文，请稍候约40秒……"):
                        # DeepSeek (OpenAI 兼容接口)：system prompt 放进 messages
                        # deepseek-v4-flash：最大输出 384K，32000 足以容纳段落式批改+双层示范，绝不截断
                        # ⚠️ 旧名 deepseek-chat 已于 2026-07-24 退役，必须用 deepseek-v4-flash
                        # 用 streaming 模式提高稳定性，避免长输出错误
                        full_text_chunks = []
                        stop_reason = None
                        stream = client.chat.completions.create(
                            model="deepseek-v4-flash",
                            # 2026-07-10 决策:评分任务必须低温。默认 1.0 导致同一篇
                            # 作文两次批改差 ±9 分;0.2 保留少量表述灵活性,分数趋稳。
                            temperature=0.2,
                            max_tokens=32000,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_msg},
                            ],
                            stream=True,
                        )
                        for chunk in stream:
                            delta = chunk.choices[0].delta.content
                            if delta:
                                full_text_chunks.append(delta)
                            fr = chunk.choices[0].finish_reason
                            if fr:
                                stop_reason = fr
                    raw = ''.join(full_text_chunks).strip()

                    # 检测是否被 max_tokens 截断
                    if stop_reason == 'length':
                        st.warning("⚠️ AI 输出过长被截断了，正在尝试修复…")

                    # 清理markdown标记
                    if "```" in raw:
                        parts = raw.split("```")
                        for part in parts:
                            part = part.strip()
                            if part.startswith("json"):
                                part = part[4:].strip()
                            if part.startswith("{"):
                                raw = part
                                break

                    # 提取 { ... } 内容
                    if not raw.strip().startswith("{"):
                        start = raw.find("{")
                        end = raw.rfind("}") + 1
                        if start != -1 and end > start:
                            raw = raw[start:end]

                    raw = raw.strip()

                    # ── 核心修复：清理JSON字符串值里的非法双引号 ──
                    # AI有时在字符串值里写了双引号，如："analysis":"他写"很脏""
                    # 用状态机扫描，把字符串值内部的裸双引号替换成中文引号
                    import re as _json_re
                    def fix_json_quotes(s):
                        result = []
                        in_string = False
                        escape_next = False
                        i = 0
                        while i < len(s):
                            c = s[i]
                            if escape_next:
                                result.append(c)
                                escape_next = False
                            elif c == '\\':
                                result.append(c)
                                escape_next = True
                            elif c == '"':
                                if not in_string:
                                    in_string = True
                                    result.append(c)
                                else:
                                    # 检查是否是合法的字符串结束符
                                    # 合法：后面跟着 : , } ] 或空白
                                    j = i + 1
                                    while j < len(s) and s[j] in ' \t\n\r':
                                        j += 1
                                    next_char = s[j] if j < len(s) else ''
                                    if next_char in ':,}]':
                                        in_string = False
                                        result.append(c)
                                    else:
                                        # 非法双引号，替换成中文引号
                                        result.append('\u201c' if len(result) > 0 else '\u201d')
                            elif c == '\n' and in_string:
                                # 字符串内的裸换行符 → 转义成 \n
                                result.append('\\n')
                            elif c == '\r' and in_string:
                                result.append('\\n')
                            else:
                                result.append(c)
                            i += 1
                        return ''.join(result)

                    def try_recover_truncated_json(s):
                        """如果 JSON 被截断，尝试关闭未关闭的字符串/对象/数组"""
                        s = s.rstrip()
                        # 找到最后一个完整的字段（以 } 或 ] 结束的）
                        # 从尾部往回找，截到最后一个有效结构处
                        last_safe = -1
                        depth_brace = 0
                        depth_bracket = 0
                        in_str = False
                        esc = False
                        for i, c in enumerate(s):
                            if esc:
                                esc = False
                                continue
                            if c == '\\':
                                esc = True
                                continue
                            if c == '"':
                                in_str = not in_str
                                continue
                            if in_str:
                                continue
                            if c == '{': depth_brace += 1
                            elif c == '}':
                                depth_brace -= 1
                                if depth_brace == 0 and depth_bracket == 0:
                                    last_safe = i + 1
                            elif c == '[': depth_bracket += 1
                            elif c == ']':
                                depth_bracket -= 1
                                if depth_brace == 0 and depth_bracket == 0:
                                    last_safe = i + 1

                        # 如果找到了完整的顶层结构
                        if last_safe > 0:
                            return s[:last_safe]

                        # 否则尝试强制闭合
                        if in_str:
                            s = s + '"'
                        # 删掉最后一个不完整的字段（找最后一个逗号）
                        last_comma = s.rfind(',')
                        if last_comma > 0:
                            s = s[:last_comma]
                        # 补上缺失的括号
                        s = s + (']' * depth_bracket) + ('}' * depth_brace)
                        return s

                    def aggressive_json_clean(s):
                        """更激进的清洗:处理常见 AI 输出错误"""
                        import re as _re
                        # 1. 把字符串内的中文双引号换成中文方括号
                        # 2. 把字符串内的英文单引号统一保留
                        # 3. 把 JSON 结构外的 markdown 代码块去掉
                        s = s.strip()
                        if s.startswith('```'):
                            # 移除 markdown 代码块标记
                            s = _re.sub(r'^```(?:json)?\s*', '', s)
                            s = _re.sub(r'\s*```$', '', s)
                        # 找到第一个 { 和最后一个 }
                        first_brace = s.find('{')
                        last_brace = s.rfind('}')
                        if first_brace >= 0 and last_brace > first_brace:
                            s = s[first_brace:last_brace + 1]
                        return s

                    def extract_partial_feedback(raw_text):
                        """终极兜底:从损坏的 JSON 里手动用正则提取关键字段"""
                        import re as _re
                        result = {}
                        # 提取 scores
                        sc_match = _re.search(r'"scores"\s*:\s*\{([^}]+)\}', raw_text)
                        if sc_match:
                            sc_str = sc_match.group(1)
                            try:
                                content = int(_re.search(r'"content"\s*:\s*(\d+)', sc_str).group(1))
                                language = int(_re.search(r'"language"\s*:\s*(\d+)', sc_str).group(1))
                                total_m = _re.search(r'"total"\s*:\s*(\d+)', sc_str)
                                total = int(total_m.group(1)) if total_m else content + language
                                result['scores'] = {'content': content, 'language': language, 'total': total}
                            except (AttributeError, ValueError):
                                pass
                        # 提取 grade_estimate
                        gm = _re.search(r'"grade_estimate"\s*:\s*"([^"]+)"', raw_text)
                        if gm: result['grade_estimate'] = gm.group(1)
                        # 提取 grade_distance
                        gd = _re.search(r'"grade_distance"\s*:\s*"([^"]+)"', raw_text)
                        if gd: result['grade_distance'] = gd.group(1)
                        # 提取 audio_script
                        au = _re.search(r'"audio_script"\s*:\s*"([^"]+)"', raw_text)
                        if au: result['audio_script'] = au.group(1)
                        # 提取 overall_suggestion
                        ov = _re.search(r'"overall_suggestion"\s*:\s*"([^"]+)"', raw_text)
                        if ov: result['overall_suggestion'] = ov.group(1)
                        # 提取 encouragement
                        en = _re.search(r'"encouragement"\s*:\s*"([^"]+)"', raw_text)
                        if en: result['encouragement'] = en.group(1)
                        # 默认空段落
                        result.setdefault('paragraph_feedback', [])
                        result.setdefault('coaching_advice', [])
                        result.setdefault('strengths', [])
                        return result

                    feedback = None
                    try:
                        feedback = json.loads(raw)
                    except json.JSONDecodeError:
                        # 第 1 层:激进清洗(去 markdown 代码块、修剪到大括号范围)
                        cleaned = aggressive_json_clean(raw)
                        try:
                            feedback = json.loads(cleaned)
                        except json.JSONDecodeError:
                            # 第 2 层:修复引号 + 换行符
                            fixed = fix_json_quotes(cleaned)
                            try:
                                feedback = json.loads(fixed)
                            except json.JSONDecodeError:
                                # 第 3 层:尝试恢复截断的 JSON
                                recovered = try_recover_truncated_json(fixed)
                                try:
                                    feedback = json.loads(recovered)
                                    st.info("✓ AI 输出被截断,已自动恢复部分内容")
                                except json.JSONDecodeError:
                                    # 第 4 层:终极兜底 — 用正则提取关键字段
                                    feedback = extract_partial_feedback(raw)
                                    if feedback.get('scores'):
                                        st.warning(
                                            "⚠️ AI 输出格式异常,已提取出分数和总评。"
                                            "段落级批改可能不完整,请重新提交一次以获得完整批改。"
                                        )
                                    else:
                                        st.error(
                                            "❌ AI 输出严重异常,无法提取批改结果。"
                                            "请稍后重新提交,或联系管理员。"
                                        )
                                        with st.expander("查看 AI 原始返回(用于调试)"):
                                            st.code(raw[:5000])
                                        st.stop()

                    # ══ 2026-07-12 决策:二语语文分下限,服务端强制钳位(双保险) ══
                    # prompt 里写了规则,但模型会漂;这里是最后一道闸。
                    try:
                        _floor_cfg = {  # exam_level 前缀 → (字数门槛, 语文下限, 语文满分)
                            'HCL': (480, 16, 30),
                            'O_CL': (320, 11, 20),
                            'N_CL': (320, 11, 20),
                            'PRACTICAL': (180, 6, 10),
                        }
                        _fkey = 'PRACTICAL' if exam_level.startswith('PRACTICAL') else exam_level
                        if _fkey in _floor_cfg and isinstance(feedback.get('scores'), dict):
                            _th, _floor, _lmax = _floor_cfg[_fkey]
                            _nchars = len(''.join(corrected_text.split()))
                            _lang = feedback['scores'].get('language')
                            if (_nchars >= _th and isinstance(_lang, (int, float))
                                    and 0 < _lang < _floor):
                                # 例外校验:AI 必须逐字引出 ≥3 处读不通的原句,且原文中真能找到
                                _exc = feedback.get('language_floor_exception') or {}
                                _quotes = _exc.get('unclear_quotes') or []
                                _norm_essay = ''.join(corrected_text.split())
                                _valid = [q for q in _quotes
                                          if isinstance(q, str)
                                          and len(''.join(q.split())) >= 4
                                          and ''.join(q.split()) in _norm_essay]
                                if not (_exc.get('applies') is True and len(_valid) >= 3):
                                    feedback['scores']['language'] = _floor
                                    _c = feedback['scores'].get('content') or 0
                                    feedback['scores']['total'] = _c + _floor
                                    feedback['language_floor_applied'] = True
                                    _gr = feedback.get('grading_rationale')
                                    if isinstance(_gr, dict):
                                        _gr['language_reason'] = (
                                            (_gr.get('language_reason') or '')
                                            + f"　※ 已按二语评分原则调整:全文 {_nchars} 字"
                                              f"达到篇幅门槛,语文分按下限 {_floor}/{_lmax} 计。")
                    except Exception:
                        pass  # 钳位逻辑任何异常都不拦批改主流程

                    from language_audit import audit_language, openai_call
                    with st.spinner("Checking language in sections（逐段复核语言）…"):
                        feedback['language_audit'] = audit_language(
                            st.session_state.get('ocr_pages') or [corrected_text],
                            openai_call(client, st.secrets.get('LANGUAGE_AUDIT_MODEL', 'deepseek-v4-flash')),
                            cache=st.session_state)
                    if not feedback['language_audit']['complete']:
                        st.warning("Language review incomplete（部分语言复核未完成）；已保留已完成结果。")

                    # 2026-07-19 决策:等级字段一致性强制统一(见 prompts.py
                    # finalize_grade_fields 注释)——与上面的语文分下限钳位同一纪律
                    try:
                        feedback = finalize_grade_fields(feedback, exam_level)
                    except Exception:
                        pass

                    sub_id = save_submission(
                        asgn['id'],
                        st.session_state['student_id'],
                        st.session_state['student_name'],
                        st.session_state['image_bytes'],
                        corrected_text,
                        feedback,
                        assignment=asgn,  # 传入作业 dict，让成长档案自动提取 exam_level/genre/题型
                        parent_submission_id=_parent_sid,
                    )
                    st.session_state['feedback'] = feedback
                    st.session_state['sub_id'] = sub_id
                    record_usage(st.session_state['code_info']['id'], sub_id,
                                 is_new_essay=(_parent_sid is None))
                    try:  # 刷新额度显示(欢迎条读 code_info)
                        st.session_state['code_info'] = get_code_info(
                            st.session_state['code_info']['id'])
                    except Exception:
                        pass
                    pm = st.session_state.get('prompt_meta', {})
                    try:
                        save_student_prompt(sub_id, pm.get('source', ''),
                                            pm.get('prompt_text', ''), pm.get('requirements', ''),
                                            pm.get('genre', ''), pm.get('school_score', ''))
                    except Exception:
                        pass  # 元数据保存失败不拖垮主流程
                    st.rerun()

                except json.JSONDecodeError:
                    st.error("AI返回格式有误，请重试。")
                    st.code(raw[:500])
                except Exception as e:
                    st.error(f"发生错误：{e}")

# ═══════════════════════════════════════════════════════════
# STAGE 3 — Show feedback (分层展示)
# ═══════════════════════════════════════════════════════════
elif st.session_state['feedback']:

    def _reset_for_new_essay():
        """清空本次提交状态,回到 Stage 1(含段落版本选择的残留键)"""
        for key in ['feedback','sub_id','ocr_done','ocr_text','ocr_pages','ocr_layout_pages',
                    'image_bytes','all_image_bytes','all_image_names','selected_assignment',
                    'student_id','student_name','tts_lang',
                    'prompt_meta','prompt_ocr','parent_submission_id']:
            st.session_state.pop(key, None)
        for key in [k for k in st.session_state.keys() if str(k).startswith('para_ver_')]:
            st.session_state.pop(key, None)
        st.session_state.pop('model_essay_ver', None)

    # 顶部备用入口:即使下方渲染出错,学生也能提交下一篇
    top_l, top_r = st.columns([5, 1])
    with top_r:
        if st.button("📝 提交另一篇", key="resubmit_top", use_container_width=True):
            _reset_for_new_essay()
            st.rerun()

    fb = st.session_state['feedback']
    sub_id = st.session_state.get('sub_id')
    lang = st.session_state.get('tts_lang', '普通话 (Mandarin)')
    name = st.session_state.get('student_name', '同学')

    if sub_id:
        mark_viewed(sub_id)

    # ── 取出新数据 ──────────────────────────────────────────
    scores = fb.get('scores', {})
    content_score = scores.get('content', 0)
    language_score = scores.get('language', 0)
    total_score = scores.get('total', content_score + language_score)

    rationale = fb.get('grading_rationale', {})
    content_level = rationale.get('content_level', '?')
    language_level = rationale.get('language_level', '?')
    content_reason = rationale.get('content_reason', '')
    language_reason = rationale.get('language_reason', '')

    grade = fb.get('grade_estimate', '')
    grade_distance = fb.get('grade_distance', '')
    audio_script = fb.get('audio_script', '')
    strengths = fb.get('strengths', [])
    overall = fb.get('overall_suggestion', '')
    encourage = fb.get('encouragement', '')
    coaching = fb.get('coaching_advice', [])
    paragraphs = fb.get('paragraph_feedback', [])
    # 整篇范文从段落 revised 自动拼起来(不依赖单独字段,节省 AI 输出 token)
    # 2026-07-12 决策:只保留高分版(提升版随 prompt 停用);没问题的段落
    # revised_top 为空(Option C),用学生原文补位——保证"整篇范文"是完整一篇,
    # 而不是只有问题段的拼贴
    if paragraphs:
        model_top = "\n\n".join([
            (p.get('revised_top') or p.get('revised_advanced')
             or p.get('original_text') or '')
            for p in paragraphs
        ]).strip()
    else:
        model_top = fb.get('model_essay_advanced', '')  # 兼容老数据

    if not audio_script:
        audio_script = f"{name}同学，{overall}。{encourage}"

    # ══════════════════════════════════════════════════════════
    # 模块 1:精简评分卡 — 顶部展示分数 + 等级
    # ══════════════════════════════════════════════════════════
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);border-radius:20px;
        padding:1.5rem 2rem;margin:1rem 0 1.5rem;color:white;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
            <div>
                <div style="font-size:1rem;color:#f0c27f;font-family:'Noto Serif SC',serif;
                    margin-bottom:0.3rem;">📋 {name} 的作文批改结果</div>
                <div style="font-size:0.85rem;color:#b8c5d6;">基于新加坡考评局（SEAB）官方评分标准</div>
            </div>
            <div style="text-align:center;background:rgba(240,194,127,0.15);padding:0.6rem 1.5rem;
                border-radius:12px;border:1px solid rgba(240,194,127,0.3);">
                <div style="font-size:0.7rem;color:#b8c5d6;margin-bottom:0.2rem;">预估等级</div>
                <div style="font-size:2.5rem;font-weight:700;color:#f0c27f;
                    font-family:'Noto Serif SC',serif;line-height:1;">{grade}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 三列分数展示
    # 根据考试段拿正确的满分值
    asgn_for_max = st.session_state.get('selected_assignment', {})
    exam_lvl_for_max = asgn_for_max.get('exam_level', 'HCL') if asgn_for_max else 'HCL'
    try:
        from prompts import EXAM_LEVELS as _EL
        _cfg = _EL.get(exam_lvl_for_max, _EL['HCL'])
        max_content = _cfg['content_max']
        max_language = _cfg['language_max']
        max_total = _cfg['essay_total']
    except:
        max_content, max_language, max_total = 30, 30, 60

    col_c, col_l, col_t = st.columns(3)
    with col_c:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:1rem;border:1px solid #e8e0d5;
            text-align:center;">
            <div style="font-size:0.8rem;color:#888;">内容</div>
            <div style="font-size:2rem;font-weight:700;color:#1a1a2e;font-family:'Noto Serif SC',serif;">
                {content_score}<span style="font-size:1rem;color:#888;">/{max_content}</span>
            </div>
            <div style="font-size:0.8rem;color:#0f3460;font-weight:500;">{content_level}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_l:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:1rem;border:1px solid #e8e0d5;
            text-align:center;">
            <div style="font-size:0.8rem;color:#888;">语文</div>
            <div style="font-size:2rem;font-weight:700;color:#1a1a2e;font-family:'Noto Serif SC',serif;">
                {language_score}<span style="font-size:1rem;color:#888;">/{max_language}</span>
            </div>
            <div style="font-size:0.8rem;color:#0f3460;font-weight:500;">{language_level}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#fdf8ee,#f5e9d3);border-radius:12px;padding:1rem;
            border:1px solid #f0c27f;text-align:center;">
            <div style="font-size:0.8rem;color:#7a5c1e;">总分</div>
            <div style="font-size:2rem;font-weight:700;color:#7a5c1e;font-family:'Noto Serif SC',serif;">
                {total_score}<span style="font-size:1rem;color:#7a5c1e;">/{max_total}</span>
            </div>
            <div style="font-size:0.8rem;color:#7a5c1e;font-weight:500;">{grade_distance[:30] if grade_distance else ''}</div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # 模块 1.15:与上一版对比(2026-07-05)— 重交作文显示分数变化
    # 数据来源:submissions.parent_submission_id;失败静默,不影响结果页
    # ══════════════════════════════════════════════════════════
    try:
        _cmp_parent = st.session_state.get('parent_submission_id')
        if _cmp_parent:
            from database import get_submission_brief
            _pb2 = get_submission_brief(_cmp_parent, st.session_state.get('student_id', ''))
            if _pb2 and _pb2.get('total') is not None and total_score is not None:
                _delta = round(float(total_score) - float(_pb2['total']), 1)
                _delta = int(_delta) if _delta == int(_delta) else _delta
                if _delta > 0:
                    _d_bg, _d_bd, _d_tx = '#e8f5e9', '#2e7d32', f'🎉 修改有效!比上一版提高了 <strong>{_delta} 分</strong>({_pb2["total"]} → {total_score})。这就是"改"的力量,继续保持!'
                elif _delta < 0:
                    _d_bg, _d_bd, _d_tx = '#fdf8ee', '#ef6c00', f'比上一版低了 {abs(_delta)} 分({_pb2["total"]} → {total_score})。别灰心,看看下面的批改,找找这次改动哪里方向偏了。'
                else:
                    _d_bg, _d_bd, _d_tx = '#f5f4f0', '#888888', f'和上一版持平({total_score} 分)。对照下面的批改,看看"最影响分数的问题"解决了没有。'
                st.markdown(
                    f'<div style="background:{_d_bg};border-left:3px solid {_d_bd};'
                    f'border-radius:6px;padding:0.6rem 1rem;margin:0.6rem 0 0;'
                    f'font-size:0.9rem;color:#2c2c2a;">🔁 修改后重交　·　{_d_tx}</div>',
                    unsafe_allow_html=True)
    except Exception:
        pass

    # ══════════════════════════════════════════════════════════
    # 模块 1.2:核心问题横幅(3 秒层) — 前端自动从段落批改挑最影响分数的一个
    # 规则:有结构内容问题 或 段落角色含负面词 = 红色段落;
    #       优先级 核心情节 > 结尾 > 开头 > 其他;同级按段落顺序。
    # ★ 定位一律用循环序号 p_idx,不用 AI 返回的 para_num(可能缺失或重复)
    # ══════════════════════════════════════════════════════════
    _BAD_ROLE_KW = ['太快', '太多', '还差', '无效', '废话', '流水账', '偏题', '不足', '缺']

    def _para_severity(p):
        """返回 'red' / 'yellow' / 'green'"""
        role = p.get('para_role', '') or ''
        struct = p.get('structure_content_issues', []) or []
        red_n = len(p.get('red_issues', []) or p.get('language_issues', []) or [])
        green_n = len(p.get('green_issues', []) or [])
        if struct or any(k in role for k in _BAD_ROLE_KW):
            return 'red'
        if red_n or green_n:
            return 'yellow'
        return 'green'

    def _para_priority(p):
        role = p.get('para_role', '') or ''
        if '核心' in role: return 0
        if '结尾' in role: return 1
        if '开头' in role: return 2
        return 3

    top_issue_idx = None
    if paragraphs:
        _tp_role = ''
        _tp_problem = ''
        # ── 首选:AI 在批改时直接指认的全文最拖分问题(v5.3 新增字段)──
        _ai_top = fb.get('top_issue') or {}
        if isinstance(_ai_top, dict) and _ai_top.get('problem'):
            try:
                _pi = int(_ai_top.get('para_index', 0)) - 1  # AI 用 1 起始的数组序号
            except Exception:
                _pi = -1
            if 0 <= _pi < len(paragraphs):
                top_issue_idx = _pi
                _tp_problem = str(_ai_top.get('problem', ''))
                _tp_role = (paragraphs[_pi].get('para_role', '') or '')
        # ── 兜底:旧记录没有 top_issue 字段时,前端按红色标签猜第一个 ──
        if top_issue_idx is None:
            _reds = [(i, p) for i, p in enumerate(paragraphs) if _para_severity(p) == 'red']
            _reds.sort(key=lambda ip: (_para_priority(ip[1]), ip[0]))
            if _reds:
                top_issue_idx, _tp = _reds[0]
                _tp_role = _tp.get('para_role', '') or ''
                _struct = _tp.get('structure_content_issues', []) or []
                _tp_problem = (_struct[0].get('problem', '') if _struct else '') or overall or ''
        if top_issue_idx is not None:
            _tp_num = paragraphs[top_issue_idx].get('para_num', top_issue_idx + 1)
            if len(_tp_problem) > 70:
                _tp_problem = _tp_problem[:70] + '…'
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#8e2020,#b3541e);border-radius:14px;
                padding:1rem 1.4rem;margin:0.8rem 0;color:white;">
                <div style="font-size:0.78rem;color:#ffd9b3;font-weight:600;margin-bottom:0.25rem;">
                    🎯 最影响你分数的一个问题</div>
                <div style="font-size:1.05rem;font-weight:600;line-height:1.6;">
                    第 {_tp_num} 段（{_tp_role}）：{_tp_problem}</div>
                <div style="font-size:0.82rem;color:#ffe3c2;margin-top:0.35rem;">
                    👇 往下点开「第 {_tp_num} 段」，老师带你一步步改。改好这一处，分数提升最快。</div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # 模块 1.3:实用文格式清单(format_check) — 仅实用文批改会返回
    # 2026-07-06 新增:逐项显示格式要件的 状态/扣分,作文批改无此字段自动跳过
    # ══════════════════════════════════════════════════════════
    _fmt_checks = fb.get('format_check') or []
    if isinstance(_fmt_checks, list) and _fmt_checks:
        from html import escape as _hesc
        _rows = ""
        _ded_total = 0
        for _fc in _fmt_checks:
            if not isinstance(_fc, dict):
                continue
            _item = _hesc(str(_fc.get('item', '') or ''))
            _status = _hesc(str(_fc.get('status', '') or ''))
            try:
                _ded = int(float(_fc.get('deduction', 0) or 0))
            except Exception:
                _ded = 0
            _note = _hesc(str(_fc.get('note', '') or ''))
            _ded_total += max(_ded, 0)
            _ok = (_ded <= 0)
            _icon = '✅' if _ok else '⚠️'
            _c = '#2e7d32' if _ok else '#c62828'
            _ded_txt = f'<span style="color:#c62828;font-weight:700;">−{_ded} 分</span>' if _ded > 0 else ''
            _rows += (
                f'<tr><td style="padding:0.3rem 0.6rem;white-space:nowrap;">{_icon} <strong>{_item}</strong></td>'
                f'<td style="padding:0.3rem 0.6rem;color:{_c};">{_status}</td>'
                f'<td style="padding:0.3rem 0.6rem;text-align:center;">{_ded_txt}</td>'
                f'<td style="padding:0.3rem 0.6rem;color:#555;font-size:0.82rem;">{_note}</td></tr>')
        if _rows:
            _sum_txt = (f'共扣 {_ded_total} 分' if _ded_total > 0 else '格式全部正确,没有扣分 🎉')
            st.markdown(f"""
            <div style="background:#fdf8ee;border:1px solid #f0c27f;border-radius:12px;
                padding:0.9rem 1.2rem;margin:0.8rem 0;">
                <div style="font-weight:700;color:#7a5c1e;margin-bottom:0.4rem;">
                    📋 实用文格式清单　·　{_sum_txt}</div>
                <table style="width:100%;border-collapse:collapse;font-size:0.9rem;color:#2c2c2a;">
                    <tr style="color:#888;font-size:0.78rem;">
                        <td style="padding:0.2rem 0.6rem;">项目</td>
                        <td style="padding:0.2rem 0.6rem;">状态</td>
                        <td style="padding:0.2rem 0.6rem;text-align:center;">扣分</td>
                        <td style="padding:0.2rem 0.6rem;">说明</td></tr>
                    {_rows}
                </table>
                <div style="font-size:0.76rem;color:#888;margin-top:0.4rem;">
                    格式类扣分计入"语文与结构"(合计最多扣 2 分);漏回应网民的扣分计入"内容"。</div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # 模块 1.5:进步卡片 — 让学生一眼看到“这次比上次进步了多少”
    # 仅在已存库(有 sub_id)时显示;同文体首篇显示起点卡,之后显示进步/提醒
    # ══════════════════════════════════════════════════════════
    if sub_id:
        try:
            _card = get_progress_card_data(
                st.session_state.get('student_id', ''), sub_id
            )
            _card_html = render_progress_card_html(_card)
            if _card_html:
                st.markdown(_card_html, unsafe_allow_html=True)
        except Exception:
            pass  # 卡片渲染失败绝不影响批改结果展示

    # ══════════════════════════════════════════════════════════
    # 模块 2:总评 + 优点 + 教练建议(语音 + 文字)
    # ══════════════════════════════════════════════════════════
    tts_voice = "zh-CN-XiaoxiaoNeural" if "普通话" in lang else "en-US-JennyNeural"

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔊 老师总评 + 进步建议（点开听老师讲）", expanded=False):
        # 语音播放 - 读完整总评(包括优点、建议、教练建议)
        try:
            import asyncio, edge_tts, io as _io
            async def _gen_audio(text, voice):
                com = edge_tts.Communicate(text, voice=voice, rate="-5%")
                buf = _io.BytesIO()
                async for chunk in com.stream():
                    if chunk["type"] == "audio": buf.write(chunk["data"])
                buf.seek(0); return buf

            # 拼接完整语音内容
            _audio_parts = [audio_script] if audio_script else []
            if strengths:
                _audio_parts.append("你的优点是：" + "；".join(strengths))
            # 2026-07-12 决策:记叙文总评必含选材评价(material_review,其他文体为空)
            _material_review = fb.get('material_review', '') or ''
            if _material_review:
                _audio_parts.append("关于选材：" + _material_review)
            if overall:
                _audio_parts.append("最重要的建议：" + overall)
            if coaching:
                _audio_parts.append("老师的教练建议是。" + "。".join(coaching))
            if encourage:
                _audio_parts.append(encourage)
            _full_audio = "。".join([p.strip().rstrip("。") for p in _audio_parts if p]) + "。"

            st.audio(asyncio.run(_gen_audio(_full_audio, tts_voice)), format="audio/mp3")
        except Exception as e:
            st.caption(f"语音暂时不可用:{e}")

        # 文字总评
        st.markdown(f"""
        <div style="background:#fdf8ee;border-radius:8px;padding:0.9rem 1rem;
            font-size:0.95rem;color:#3a3020;margin:0.8rem 0;border-left:3px solid #f0c27f;">
            💬 {audio_script}
        </div>""", unsafe_allow_html=True)

        # 优点 - 1-2 句简洁带过
        if strengths:
            strengths_text = " · ".join(strengths)
            st.markdown(f"""
            <div style="background:#e8f5e9;border-radius:8px;padding:0.7rem 1rem;
                margin:0.5rem 0;border-left:3px solid #43a047;">
                <span style="color:#2e7d32;font-weight:600;font-size:0.85rem;">✅ 优点：</span>
                <span style="color:#1b5e20;font-size:0.9rem;">{strengths_text}</span>
            </div>""", unsafe_allow_html=True)

        # 选材点评(2026-07-12 决策:记叙文总评必含"选材"评价——选材三问:
        # 合生活逻辑/扣题目逻辑/概念没偷换;其他文体该字段为空,自动不显示)
        _mat_rev = fb.get('material_review', '') or ''
        if _mat_rev:
            st.markdown(f"""
            <div style="background:#ede7f6;border-radius:8px;padding:0.7rem 1rem;
                margin:0.5rem 0;border-left:3px solid #5e35b1;">
                <span style="color:#4527a0;font-weight:600;font-size:0.85rem;">📌 选材点评：</span>
                <span style="color:#311b92;font-size:0.9rem;">{_mat_rev}</span>
            </div>""", unsafe_allow_html=True)

        # 整体建议
        if overall:
            st.markdown(f"""
            <div style="background:#fff3e0;border-radius:8px;padding:0.7rem 1rem;
                margin:0.5rem 0;border-left:3px solid #fb8c00;">
                <span style="color:#e65100;font-weight:600;font-size:0.85rem;">🎯 最重要的建议：</span>
                <span style="color:#5d3700;font-size:0.9rem;">{overall}</span>
            </div>""", unsafe_allow_html=True)

        # 教练式建议
        if coaching:
            coaching_html = "".join([
                f'<div style="color:#1a3a5c;font-size:0.9rem;margin:0.3rem 0;padding-left:1rem;">→ {c}</div>'
                for c in coaching
            ])
            st.markdown(f"""
            <div style="background:#e3f2fd;border-radius:8px;padding:0.8rem 1rem;
                margin:0.5rem 0;border-left:3px solid #1e88e5;">
                <div style="color:#0d47a1;font-weight:600;font-size:0.9rem;margin-bottom:0.4rem;">
                    📝 老师的教练建议
                </div>
                {coaching_html}
            </div>""", unsafe_allow_html=True)

        # 鼓励语
        if encourage:
            st.markdown(f"""
            <div style="background:#f3e5f5;border-radius:8px;padding:0.7rem 1rem;
                margin:0.5rem 0;border-left:3px solid #8e24aa;">
                <span style="color:#6a1b9a;font-weight:600;font-size:0.85rem;">💖 </span>
                <span style="color:#4a148c;font-size:0.9rem;font-style:italic;">{encourage}</span>
            </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # 模块 3:评分依据(可折叠,默认折叠 — 让学生看主要的)
    # ══════════════════════════════════════════════════════════
    with st.expander("📊 评分依据（按 SEAB 官方等级标准）", expanded=False):
        st.markdown(f"""
        <div style="background:white;border-radius:8px;padding:0.9rem 1rem;margin:0.4rem 0;
            border:1px solid #e8e0d5;">
            <div style="color:#0f3460;font-weight:600;font-size:0.9rem;margin-bottom:0.3rem;">
                内容 {content_score}分 — {content_level}
            </div>
            <div style="color:#555;font-size:0.85rem;line-height:1.6;">{content_reason}</div>
        </div>
        <div style="background:white;border-radius:8px;padding:0.9rem 1rem;margin:0.4rem 0;
            border:1px solid #e8e0d5;">
            <div style="color:#0f3460;font-weight:600;font-size:0.9rem;margin-bottom:0.3rem;">
                语文 {language_score}分 — {language_level}
            </div>
            <div style="color:#555;font-size:0.85rem;line-height:1.6;">{language_reason}</div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # 模块 4:段落式批改(v3 核心 — 阶段 A:简化版,阶段 B 升级为左右对照)
    # ══════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2026-07-08 修复:以下工具函数提到区块作用域 ──
    #    (模块5"整篇范文对比"也用它们;新视图跳过旧视图时曾触发 NameError)
    def html_escape(s):
        """HTML 转义"""
        return (str(s).replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;').replace('"', '&quot;'))

    _STRUCT_TAG_COLORS = {
        "论点": "#c62828", "解释": "#ef6c00", "举例": "#2e7d32",
        "分析": "#1565c0", "扣题": "#6a1b9a",
        "铺垫": "#5d4037", "环境": "#00695c", "动作": "#2e7d32",
        "心理": "#1565c0", "对话": "#ef6c00", "细节": "#c62828",
        "抒情": "#6a1b9a", "点题": "#8e24aa",
        "问候": "#00695c", "身份": "#5d4037", "目的": "#c62828",
        "回应": "#ef6c00", "观点": "#1565c0", "原因": "#2e7d32",
        "建议": "#6a1b9a", "结束": "#8e24aa",
    }

    def render_revised_html(text):
        """转义 + 把【已知功能标签】渲染成彩色徽章;未知【】内容原样保留"""
        import re as _re2
        esc = html_escape(text)

        def _rep(m):
            tag = m.group(1)
            color = _STRUCT_TAG_COLORS.get(tag)
            if not color:
                return m.group(0)
            return (f'<span style="background:{color}18;color:{color};'
                    f'border:1px solid {color};border-radius:3px;font-size:0.68rem;'
                    f'padding:0 0.3rem;margin:0 0.2rem 0 0.1rem;font-weight:600;'
                    f'vertical-align:0.08em;white-space:nowrap;">{tag}</span>')

        return _re2.sub(r'【([^【】]{1,6})】', _rep, esc)

    def _has_struct_tags(text):
        import re as _re3
        for _m in _re3.finditer(r'【([^【】]{1,6})】', str(text or '')):
            if _m.group(1) in _STRUCT_TAG_COLORS:
                return True
        return False

    # ═══════════════════════════════════════════════════════════
    # 2026-07-12(晚) 决策:错字病句展示分两处——
    #   ① 作文照片上直接画记号(image_review_page,覆盖优先,位置允许略偏);
    #   ② 模块5"整篇范文对比"左栏原文里画红线,悬停看正确写法(逐字匹配,永远准)。
    #   右栏段落卡只放内容解说 + 高分版,不混入错字列表(否则右栏太乱)。
    # ═══════════════════════════════════════════════════════════
    def _collect_red_issues(_fb):
        """跨段收集全部错字病句(红类)。弱句/逻辑/衔接归绿类,不画红线。"""
        reds = []
        for _p in (_fb.get('paragraph_feedback') or []):
            for _it in (_p.get('red_issues') or []):
                if _it.get('original'):
                    reds.append(_it)
            for _it in (_p.get('issues') or []):        # 旧字段兼容
                _t = _it.get('type', '')
                if _it.get('original') and not any(
                        k in _t for k in ['弱句', '逻辑', '衔接']):
                    reds.append(_it)
        if not reds:                                    # 更旧数据:全局 annotations
            for _a in (_fb.get('annotations') or []):
                if _a.get('quote') and _a.get('action') in ('replace', 'delete'):
                    reds.append({'original': _a['quote'],
                                 'improved': _a.get('fix', ''),
                                 'explanation': _a.get('comment', '')})
        return reds

    def _redline_fulltext_html(full_text, reds):
        """整篇原文 + 红线标注。铁律:引文逐字匹配不上就跳过该条,绝不错标。"""
        repl = []
        for _r in reds:
            _tgt = _r.get('original', '')
            if not _tgt or _tgt not in full_text:
                continue
            _imp = html_escape(_r.get('improved', '') or _r.get('suggestion', ''))
            _why = html_escape(_r.get('explanation', '') or _r.get('issue_detail', ''))
            _hl = (f'<span class="red-hl">{html_escape(_tgt)}'
                   f'<span class="tooltip-content"><b>正确写法：</b>{_imp}<br>'
                   f'<span style="font-size:0.75rem;color:#aaa;">💡 {_why}</span>'
                   f'</span></span>')
            _st = 0
            while True:
                _k = full_text.find(_tgt, _st)
                if _k < 0:
                    break
                repl.append((_k, _k + len(_tgt), _hl))
                _st = _k + len(_tgt)
        repl.sort(key=lambda x: x[0])
        out, cur, last_end = [], 0, -1
        for _s, _e, _h in repl:
            if _s < last_end:
                continue                                # 重叠时保留先出现的
            out.append(html_escape(full_text[cur:_s]))
            out.append(_h)
            cur = _e
            last_end = _e
        out.append(html_escape(full_text[cur:]))
        return ''.join(out)

    _REDLINE_CSS = '''<style>
    .red-hl{background:#ffebee;color:#c62828;padding:0.05rem 0.2rem;border-radius:3px;
      border-bottom:2px solid #c62828;cursor:help;position:relative;display:inline-block;}
    .red-hl:hover{background:#ffcdd2;}
    .red-hl .tooltip-content{visibility:hidden;opacity:0;position:absolute;bottom:125%;
      left:50%;transform:translateX(-50%);background:#1a1a2e;color:white;
      padding:0.6rem 0.8rem;border-radius:6px;font-size:0.85rem;white-space:normal;
      min-width:180px;max-width:280px;text-align:left;line-height:1.6;z-index:9999;
      box-shadow:0 4px 12px rgba(0,0,0,0.3);transition:opacity 0.2s;pointer-events:none;}
    .red-hl:hover .tooltip-content{visibility:visible;opacity:1;}
    </style>'''

    # ── 2026-07-12(晚) 决策:原图视图与字级圈画彻底解耦——有照片一律走"左图右评"
    #    (左=作文照片[圈画开着就带记号],右=内容解说+高分版);
    #    纯文字提交/照片缺失/未预期异常才落回下方旧文字视图。
    _new_view_shown = False
    try:
        from image_review_page import render_image_review
        _all_imgs = st.session_state.get('all_image_bytes') or []
        if not _all_imgs and st.session_state.get('image_bytes'):
            _all_imgs = [st.session_state['image_bytes']]
        # ── 2026-07-12 决策:接通"按我的原文重新批改"回调,每篇限重批 1 次 ──
        def _regrade_cb(_eid, _fixed):
            _flag = f"regrade_done_{_eid}"
            if st.session_state.get(_flag):
                st.warning("每篇作文只能按原文重批一次。如识别错误仍然很多,"
                           "请回到上一步重新上传更清晰的照片。")
                return
            st.session_state[_flag] = True
            # _fixed:list=各页分开的修正文本(多页);str=整篇(单页/旧调用)
            if isinstance(_fixed, list):
                _pages_fixed = [p or '' for p in _fixed]
            else:
                _pages_fixed = [_fixed or '']
            sync_corrected_pages(st.session_state, _pages_fixed)
            # sync_corrected_pages invalidates only changed page geometry.
            # 以"重交"身份走完整批改流程:计入总次数,不占新作文额度
            st.session_state['parent_submission_id'] = sub_id
            st.session_state['feedback'] = None
            st.session_state['sub_id'] = None
            st.session_state['ocr_done'] = True
            st.session_state['regrade_autorun'] = True   # Stage 2 自动提交

        _new_view_shown = render_image_review(
            fb=fb,
            image_bytes=st.session_state.get('image_bytes') or b'',
            ocr_text=st.session_state.get('ocr_text', ''),
            score_text=f"{total_score} / {max_total}",
            essay_id=str(sub_id or 'na'),
            regrade_cb=_regrade_cb,                     # 2026-07-12 已接通,限1次
            all_image_bytes=_all_imgs,                  # 多页:全部照片
            ocr_pages=st.session_state.get('ocr_pages'),  # 多页:各页OCR文本
            ocr_layout_pages=st.session_state.get('ocr_layout_pages'),  # GLM-OCR官方bbox
        )
    except Exception:
        _new_view_shown = False

    if not _new_view_shown:
        st.markdown("### 📖 逐段批改与修改示范")

    if _new_view_shown:
        pass                                            # 新视图已渲染,跳过旧视图
    elif not paragraphs:
        st.info("AI 没有返回段落级批改。请检查作文内容。")
    else:

        # ── HTML 工具函数:在原文里嵌入红绿高亮 ────────────
        def html_escape(s):
            """HTML 转义"""
            return (str(s).replace('&', '&amp;').replace('<', '&lt;')
                    .replace('>', '&gt;').replace('"', '&quot;'))

        # 示范段句子功能标签(2026-07-05):AI 在 revised 文字里用【标签】标注句子功能,
        # 前端把已知标签渲染成小徽章,让学生看到好段落是怎么搭起来的
        _STRUCT_TAG_COLORS = {
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

        def render_revised_html(text):
            """转义 + 把【已知功能标签】渲染成彩色徽章;未知【】内容原样保留"""
            import re as _re2
            esc = html_escape(text)

            def _rep(m):
                tag = m.group(1)
                color = _STRUCT_TAG_COLORS.get(tag)
                if not color:
                    return m.group(0)
                return (f'<span style="background:{color}18;color:{color};'
                        f'border:1px solid {color};border-radius:3px;font-size:0.68rem;'
                        f'padding:0 0.3rem;margin:0 0.2rem 0 0.1rem;font-weight:600;'
                        f'vertical-align:0.08em;white-space:nowrap;">{tag}</span>')

            return _re2.sub(r'【([^【】]{1,6})】', _rep, esc)

        def _has_struct_tags(text):
            """检测文本里是否真的有已知功能标签 — 没有就不显示'彩色小标签'图例,
            避免 AI 偶尔漏输出标签时,学生看到说明却找不到标签"""
            import re as _re3
            for _m in _re3.finditer(r'【([^【】]{1,6})】', str(text or '')):
                if _m.group(1) in _STRUCT_TAG_COLORS:
                    return True
            return False

        def build_highlighted_paragraph(orig_text, red_list, green_list):
            """
            把 original_text 转成带高亮的 HTML。
            红色 = 错字病句（用 <span class="red-hl"> 包裹,鼠标悬停看正确答案）
            绿色 = 弱句逻辑（用 <span class="green-hl"> 包裹,点击展开看分析,在右侧）
            """
            # 收集所有需要高亮的"片段 → HTML"映射
            replacements = []  # (start, end, replacement_html)

            for r in red_list:
                target = r.get('original', '')
                if not target or target not in orig_text:
                    continue
                improved = html_escape(r.get('improved', ''))
                explain = html_escape(r.get('explanation', ''))
                tooltip = f"{improved}　{explain}".strip().rstrip('　')
                hl_html = (f'<span class="red-hl" data-tooltip="{tooltip}">'
                           f'{html_escape(target)}'
                           f'<span class="tooltip-content">'
                           f'<b>正确写法：</b>{improved}<br>'
                           f'<span style="font-size:0.75rem;color:#aaa;">💡 {explain}</span>'
                           f'</span></span>')
                # 找所有匹配位置
                start = 0
                while True:
                    idx = orig_text.find(target, start)
                    if idx == -1:
                        break
                    replacements.append((idx, idx + len(target), hl_html))
                    start = idx + len(target)

            for idx_g, g in enumerate(green_list):
                target = g.get('original', '')
                if not target or target not in orig_text:
                    continue
                hl_html = (f'<span class="green-hl" data-green-idx="{idx_g+1}">'
                           f'{html_escape(target)}'
                           f'<sup class="green-num">{idx_g+1}</sup>'
                           f'</span>')
                start = 0
                while True:
                    idx = orig_text.find(target, start)
                    if idx == -1:
                        break
                    replacements.append((idx, idx + len(target), hl_html))
                    start = idx + len(target)

            # 按 start 位置排序,避免重叠 — 后插入不能覆盖前一个
            replacements.sort(key=lambda x: x[0])
            # 去重:如果两段重叠,优先红色（先 append 的）
            non_overlap = []
            last_end = -1
            for s, e, html in replacements:
                if s >= last_end:
                    non_overlap.append((s, e, html))
                    last_end = e

            # 从后往前替换以保持索引有效
            result_chunks = []
            cursor = 0
            for s, e, html in non_overlap:
                if s > cursor:
                    result_chunks.append(html_escape(orig_text[cursor:s]))
                result_chunks.append(html)
                cursor = e
            if cursor < len(orig_text):
                result_chunks.append(html_escape(orig_text[cursor:]))

            return ''.join(result_chunks)

        # ── 全局 CSS:高亮样式 + 鼠标悬停 tooltip ─────────────
        st.markdown('''
        <style>
        .red-hl {
            background: #ffebee;
            color: #c62828;
            padding: 0.05rem 0.2rem;
            border-radius: 3px;
            border-bottom: 2px solid #c62828;
            cursor: help;
            position: relative;
            display: inline-block;
        }
        .red-hl:hover { background: #ffcdd2; }
        .red-hl .tooltip-content {
            visibility: hidden;
            opacity: 0;
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: #1a1a2e;
            color: white;
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            white-space: normal;
            min-width: 180px;
            max-width: 280px;
            text-align: left;
            line-height: 1.6;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: opacity 0.2s;
            pointer-events: none;
        }
        .red-hl:hover .tooltip-content {
            visibility: visible;
            opacity: 1;
        }
        .green-hl {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 0.05rem 0.2rem;
            border-radius: 3px;
            border-bottom: 2px solid #43a047;
            cursor: pointer;
            display: inline-block;
        }
        .green-hl:hover { background: #c8e6c9; }
        .green-num {
            background: #43a047;
            color: white;
            font-size: 0.65rem;
            padding: 0 0.3rem;
            border-radius: 50%;
            margin-left: 0.15rem;
            font-weight: bold;
            vertical-align: super;
        }
        .para-card {
            background: linear-gradient(135deg,#1a1a2e,#16213e);
            border-radius: 10px 10px 0 0;
            padding: 0.7rem 1rem;
            color: #f0c27f;
            font-family: 'Noto Serif SC', serif;
            font-size: 1rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: -0.5rem;
        }
        .left-orig {
            background: #fafaf0;
            border: 1px solid #e8e0d5;
            border-top: none;
            padding: 1rem 1.2rem;
            font-size: 0.95rem;
            line-height: 2.1;
            color: #2c2c2a;
            border-radius: 0;
            min-height: 250px;
            height: 100%;
        }
        .right-fb {
            background: #fbfbfb;
            border: 1px solid #e8e0d5;
            border-top: none;
            padding: 1rem 1.2rem;
            font-size: 0.92rem;
            color: #2c2c2a;
            min-height: 250px;
            height: 100%;
        }
        .legend-tag {
            display: inline-block;
            font-size: 0.72rem;
            padding: 0.1rem 0.5rem;
            border-radius: 3px;
            margin-right: 0.4rem;
            font-weight: 500;
        }
        </style>
        ''', unsafe_allow_html=True)

        # ── 全局图例提示 ──
        st.markdown(
            '<div style="background:#fdf8ee;border-left:3px solid #f0c27f;'
            'padding:0.5rem 1rem;border-radius:6px;margin-bottom:1rem;font-size:0.83rem;color:#5d3700;">'
            '<span class="legend-tag" style="background:#ffebee;color:#c62828;border:1px solid #c62828;">Red</span>'
            '错字 / 病句（悬停看正确写法）　　'
            '<span class="legend-tag" style="background:#e8f5e9;color:#2e7d32;border:1px solid #43a047;">Green</span>'
            '弱句 / 逻辑 / 衔接（编号对应右侧）'
            '</div>',
            unsafe_allow_html=True
        )

        # ── 逐段渲染:按自然段顺序,每段折叠卡 ────────────
        # ★ widget key 一律用循环序号 p_idx,不用 AI 返回的 para_num
        #   (para_num 缺失或重复会导致 DuplicateElementKey,整页崩溃,
        #    底部"提交另一篇"按钮渲染不出来,学生被卡死在结果页)
        # ★ 2026-07-05 决策:不按严重度重排,保持原文阅读顺序;
        #   问题严重度用每张卡标题上的 🔴🟡🟢 标记体现
        for p_idx, p in enumerate(paragraphs):
            _grp = _para_severity(p)
            para_num = p.get('para_num', p_idx + 1)
            para_role = p.get('para_role', '')
            original = p.get('original_text', '')
            # 兼容老数据:有些可能还是 language_issues
            red_list = p.get('red_issues', []) or []
            green_list = p.get('green_issues', []) or []
            if not red_list and not green_list and 'language_issues' in p:
                # 老结构:把所有 language_issues 当成红色
                old_iss = p.get('language_issues', [])
                for it in old_iss:
                    t = it.get('type', '')
                    if any(k in t for k in ['弱句', '逻辑', '衔接']):
                        green_list.append({
                            'type': t, 'original': it.get('original', ''),
                            'issue_detail': it.get('explanation', ''),
                            'suggestion': it.get('improved', '')
                        })
                    else:
                        red_list.append(it)

            struct_iss = p.get('structure_content_issues', [])
            highlights = p.get('highlights', '')
            why_and_how = p.get('why_and_how', '')
            # 2026-07-12 决策:基础版/提升版停用,只读高分版(旧数据回退 revised_advanced)
            revised_t = p.get('revised_top') or p.get('revised_advanced', '')

            # 折叠卡标题:段号 + 角色 + 一行结论(30秒层)
            _emoji = {'red': '🔴', 'yellow': '🟡', 'green': '🟢'}[_grp]
            if struct_iss:
                _one_line = struct_iss[0].get('problem', '') or ''
            elif red_list or green_list:
                _one_line = f"{len(red_list) + len(green_list)} 处错字病句 / 弱句"
            else:
                _one_line = highlights or '写得不错'
            if len(_one_line) > 32:
                _one_line = _one_line[:32] + '…'
            _is_top = (top_issue_idx is not None and p_idx == top_issue_idx)
            _exp_title = f"{_emoji} 第 {para_num} 段 · {para_role} ｜ {_one_line}"
            if _is_top:
                _exp_title += "　🎯 先改这里"

            # ── 整个段落收进折叠卡(3分钟层,默认只展开核心问题段) ──
            with st.expander(_exp_title, expanded=_is_top):
                # 左右两列 — 1:2 比例,左原文 / 右全部批改
                col_left, col_right = st.columns([1, 2], gap="small")

                with col_left:
                    highlighted = build_highlighted_paragraph(original, red_list, green_list)
                    st.markdown(
                        f'<div class="left-orig">'
                        f'<div style="font-size:0.75rem;color:#888;margin-bottom:0.6rem;font-weight:600;">'
                        f'📝 你的原文</div>'
                        f'<div>{highlighted}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with col_right:
                    # ─────── 右栏纯 HTML 部分(亮点 + 不足 + 绿色弱句) ───────
                    right_parts = ['<div class="right-fb">']

                    # 1. Strengths(紧凑一行)
                    if highlights:
                        right_parts.append(
                            '<div style="background:#e8f5e9;border-left:3px solid #43a047;'
                            'padding:0.35rem 0.7rem;margin-bottom:0.4rem;border-radius:4px;'
                            'font-size:0.83rem;line-height:1.5;">'
                            f'<b style="color:#2e7d32;">Strengths：</b>'
                            f'<span style="color:#1b5e20;">{html_escape(highlights)}</span>'
                            '</div>'
                        )

                    # 2. 不足:错字病句简短一行(详情看左边悬停)
                    if red_list:
                        right_parts.append(
                            '<div style="background:#ffebee;border-left:3px solid #c62828;'
                            'padding:0.35rem 0.7rem;margin-bottom:0.4rem;border-radius:4px;'
                            'font-size:0.83rem;line-height:1.5;">'
                            f'<b style="color:#c62828;">不足：</b>'
                            f'<span style="color:#5d3700;">{len(red_list)} 处错字 / 病句</span>'
                            '<span style="color:#888;font-size:0.75rem;margin-left:0.4rem;">'
                            '（鼠标悬停左边红色字看正确写法）</span>'
                            '</div>'
                        )

                    # 2026-07-13 决策(信息负担简化):绿色弱句只留一行数量提示,
                    # 详情(逐条 Issue/Suggestion)收进下方"查看详细问题清单"折叠层——
                    # 默认可见层只留"为什么改+改成什么样"(讲解区 + 高分版),
                    # 其余细项属于"想深挖才看"的第二层。
                    if green_list:
                        right_parts.append(
                            '<div style="background:#f1f8e9;border-left:3px solid #43a047;'
                            'padding:0.35rem 0.7rem;margin-bottom:0.4rem;border-radius:4px;'
                            'font-size:0.83rem;line-height:1.5;">'
                            f'<b style="color:#2e7d32;">可以更好：</b>'
                            f'<span style="color:#33691e;">{len(green_list)} 处弱句 / 表达（详情见下方"详细问题清单"）</span>'
                            '</div>'
                        )

                    right_parts.append('</div>')  # close right-fb
                    st.markdown(''.join(right_parts), unsafe_allow_html=True)

                    # ─────── 结构内容批改:语音先统一收集(不受折叠影响),
                    #         详情卡片(Issue/Suggestion/Example)收进折叠层 ───────
                    _voice_zh_parts, _voice_en_parts = [], []
                    for si in struct_iss:
                        if si.get('voice_zh'):
                            _voice_zh_parts.append(si['voice_zh'])
                        if si.get('voice_en'):
                            _voice_en_parts.append(si['voice_en'])

                    if green_list or struct_iss:
                        _detail_n = len(green_list) + len(struct_iss)
                        if st.toggle(f"🔍 查看详细问题清单（{_detail_n} 条）",
                                     key=f"tg_detail_{p_idx}"):
                            for i, g in enumerate(green_list):
                                g_orig = html_escape(g.get('original', ''))
                                g_detail = html_escape(g.get('issue_detail', ''))
                                g_sugg = html_escape(g.get('suggestion', ''))
                                st.markdown(
                                    '<div style="background:#f1f8e9;border-radius:5px;'
                                    'padding:0.45rem 0.7rem;margin:0.3rem 0;font-size:0.83rem;'
                                    'border-left:3px solid #43a047;line-height:1.55;">'
                                    f'<div style="color:#2e7d32;font-weight:600;margin-bottom:0.15rem;font-size:0.78rem;">'
                                    f'<span style="background:#43a047;color:white;border-radius:50%;'
                                    f'padding:0 0.35rem;font-size:0.7rem;margin-right:0.4rem;">{i+1}</span>'
                                    f'「{g_orig}」'
                                    f'</div>'
                                    f'<div style="color:#5d3700;margin:0.15rem 0;"><b>Issue：</b>{g_detail}</div>'
                                    f'<div style="color:#1b5e20;"><b>Suggestion：</b>{g_sugg}</div>'
                                    '</div>', unsafe_allow_html=True
                                )

                            for si in struct_iss:
                                si_aspect = si.get('aspect', '')
                                si_problem = si.get('problem', '')
                                si_sugg = si.get('suggestion', '')
                                si_example = si.get('example', '')

                                si_html = (
                                    '<div style="background:#e3f2fd;border-radius:5px;'
                                    'padding:0.5rem 0.7rem;margin:0.3rem 0;font-size:0.85rem;'
                                    'border-left:3px solid #1565c0;">'
                                    f'<div style="color:#0d47a1;font-weight:600;margin-bottom:0.3rem;font-size:0.85rem;">'
                                    f'📐 {html_escape(si_aspect)}</div>'
                                    f'<div style="color:#5d3700;margin:0.2rem 0;"><b>Issue：</b>{html_escape(si_problem)}</div>'
                                    f'<div style="color:#1b5e20;margin:0.2rem 0;"><b>Suggestion：</b>{html_escape(si_sugg)}</div>'
                                )
                                if si_example:
                                    si_html += (
                                        '<div style="background:white;border-radius:4px;'
                                        'padding:0.4rem 0.6rem;margin-top:0.3rem;border:1px solid #c5d4e3;'
                                        'font-size:0.82rem;">'
                                        '<b style="color:#0d47a1;">Example：</b>'
                                        f'<span style="color:#2c2c2a;line-height:1.6;">{html_escape(si_example)}</span>'
                                        '</div>'
                                    )
                                si_html += '</div>'
                                st.markdown(si_html, unsafe_allow_html=True)

                    # ── 2026-07-12 决策:提升版停用,示范只出高分版(见下方) ──

                    # 分隔线
                    st.markdown(
                        '<div style="border-top:1px dashed #d4e3f5;margin:0.8rem 0 0.5rem;"></div>',
                        unsafe_allow_html=True
                    )

                    # ─────── 🎧 老师讲解区(2026-07-05):语音为主,文字默认收起 ───────
                    # 中文语音 = 各问题讲解 + 为什么改怎么改,一次听完;
                    # 屏幕上只留一行提示,想读文字的学生点"📖 看文字版"
                    _zh_full = "。".join(
                        [t.strip().rstrip("。") for t in
                         (_voice_zh_parts + ([why_and_how] if why_and_how else [])) if t]
                    )
                    _en_full = " ".join([t.strip() for t in _voice_en_parts if t])
                    if _zh_full or _en_full:
                        st.markdown(
                            '<div style="background:#fff8e1;border-left:3px solid #f0c27f;'
                            'padding:0.45rem 0.9rem;margin:0.5rem 0 0.2rem;border-radius:5px;'
                            'font-size:0.85rem;color:#8a6d1e;font-weight:600;">'
                            '💡 为什么要改？怎么改？—— 点 🔊 听老师讲给你</div>',
                            unsafe_allow_html=True
                        )
                        lv1, lv2, lv3 = st.columns(3)
                        with lv1:
                            if _zh_full and st.toggle("🔊 中文讲解", key=f"tg_zh_{p_idx}"):
                                try:
                                    import asyncio, edge_tts, io as _io
                                    async def _gen_zh(text):
                                        com = edge_tts.Communicate(
                                            text, voice="zh-CN-XiaoxiaoNeural", rate="-5%"
                                        )
                                        buf = _io.BytesIO()
                                        async for c in com.stream():
                                            if c["type"] == "audio": buf.write(c["data"])
                                        buf.seek(0); return buf
                                    st.audio(asyncio.run(_gen_zh(_zh_full + "。")), format="audio/mp3")
                                except Exception as e:
                                    st.caption(f"语音不可用：{e}")
                                    st.write(_zh_full)
                        with lv2:
                            if _en_full and st.toggle("🔊 English", key=f"tg_en_{p_idx}"):
                                try:
                                    import asyncio, edge_tts, io as _io
                                    async def _gen_en(text):
                                        com = edge_tts.Communicate(
                                            text, voice="en-US-JennyNeural", rate="-5%"
                                        )
                                        buf = _io.BytesIO()
                                        async for c in com.stream():
                                            if c["type"] == "audio": buf.write(c["data"])
                                        buf.seek(0); return buf
                                    st.audio(asyncio.run(_gen_en(_en_full)), format="audio/mp3")
                                except Exception as e:
                                    st.caption(f"Audio unavailable: {e}")
                                    st.write(_en_full)
                        with lv3:
                            st.toggle("📖 看文字版", key=f"tg_txt_{p_idx}")
                        if st.session_state.get(f"tg_txt_{p_idx}") and why_and_how:
                            st.markdown(
                                f'<div style="background:#fff8e1;border-left:3px solid #f0c27f;'
                                f'padding:0.7rem 0.9rem;margin:0.3rem 0 0.6rem;border-radius:5px;'
                                f'color:#3a3020;font-size:0.88rem;line-height:1.8;">'
                                f'{html_escape(why_and_how)}</div>',
                                unsafe_allow_html=True
                            )

                    # 2026-07-12 决策:只出高分版;没问题的段 revised_top 为空,不硬凑示范
                    if revised_t:
                        _tag_hint = (
                            '<span style="font-weight:400;color:#888;font-size:0.72rem;">'
                            '彩色小标签 = 这个句子在段落里的作用</span>'
                            if _has_struct_tags(revised_t) else ''
                        )
                        st.markdown(
                            f'<div style="background:#fdecea;border-left:3px solid #c62828;'
                            f'padding:0.7rem 0.9rem;margin:0.4rem 0 0;border-radius:5px;">'
                            f'<div style="color:#c62828;font-weight:500;font-size:0.78rem;'
                            f'margin-bottom:0.3rem;">📝 🔴 高分版 · 冲 A1 的写法　{_tag_hint}</div>'
                            f'<div style="color:#2c2c2a;font-size:0.88rem;line-height:1.9;">'
                            f'{render_revised_html(revised_t)}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

            # 段落间距
            st.markdown('<div style="margin-bottom:1.5rem;"></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # 模块 5:整篇范文 + 原文对比
    # ══════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    if paragraphs:
        student_full_text = st.session_state.get('ocr_text', '')

        # 2026-07-12(晚) 决策:双版本切换删除,只出高分版;
        # 左栏原文画出【全部错字病句】(红线,悬停看正确写法)——
        # 照片记号位置允许略偏,这里的红线逐字匹配,是"永远准"的那一份
        with st.expander("📖 整篇范文对比（点开看完整示范全文）", expanded=False):
            if model_top:
                col_orig, col_revised = st.columns(2)
                with col_orig:
                    _reds_all = _collect_red_issues(fb)
                    _marked_full = _redline_fulltext_html(student_full_text, _reds_all)
                    st.markdown(
                        _REDLINE_CSS +
                        '<div style="background:#fafaf0;border-left:4px solid #888;'
                        'padding:1rem 1.2rem;border-radius:8px;font-size:0.92rem;'
                        'line-height:1.85;color:#2c2c2a;white-space:pre-wrap;'
                        'min-height:300px;">'
                        '<div style="font-size:0.8rem;color:#666;font-weight:600;margin-bottom:0.6rem;">'
                        '📝 你的原文　'
                        '<span style="font-weight:400;color:#c62828;font-size:0.72rem;">'
                        '红线 = 错字病句，鼠标悬停看正确写法</span>'
                        '</div>'
                        f'{_marked_full}'
                        '</div>',
                        unsafe_allow_html=True
                    )
                with col_revised:
                    st.markdown(
                        '<div style="background:#fdecea;border-left:4px solid #c62828;'
                        'padding:1rem 1.2rem;border-radius:8px;font-size:0.92rem;'
                        'line-height:1.85;color:#2c2c2a;white-space:pre-wrap;'
                        'min-height:300px;">'
                        '<div style="font-size:0.8rem;color:#c62828;font-weight:600;margin-bottom:0.6rem;">'
                        '✨ 高分版范文　'
                        + ('<span style="font-weight:400;color:#888;font-size:0.72rem;">'
                           '彩色小标签 = 句子在段落里的作用</span>'
                           if _has_struct_tags(model_top) else '')
                        + '</div>'
                        f'{render_revised_html(model_top)}'
                        '</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("范文未生成,请重新提交。")

    # ══════════════════════════════════════════════════════════
    # 模块 5.6:导出学习报告 PDF(2026-07-05)
    # - 按 sub_id 缓存,避免语音开关等 rerun 时重复生成
    # - 生成失败绝不影响结果页(整块 try/except 包裹)
    # ══════════════════════════════════════════════════════════
    try:
        from pdf_report import build_pdf_report
        _pdf_key = f"pdf_bytes_{sub_id or 'nosub'}"
        if _pdf_key not in st.session_state:
            _cfg_pdf = {'name': '', 'content_max': max_content,
                        'language_max': max_language, 'essay_total': max_total}
            try:
                from prompts import EXAM_LEVELS as _EL2
                _cfg_pdf['name'] = _EL2.get(exam_lvl_for_max, {}).get('name', '')
            except Exception:
                pass
            _asgn_pdf = st.session_state.get('selected_assignment', {}) or {}
            _prompt_title = _asgn_pdf.get('prompt', '') or _asgn_pdf.get('title', '')
            if _prompt_title == "(学生未提供题目)":
                _prompt_title = ''
            # ── 2026-07-12 决策(方案A):优先生成"左图右评"版报告 ──
            # 照片不入库,只有批改当次会话内存里还有照片时才做得出图文版;
            # 学生日后回来重下时照片已不在,自动退回纯文字版。
            _pdf_bytes = None
            try:
                _imgs_pdf = st.session_state.get('all_image_bytes') or []
                _pages_pdf = st.session_state.get('ocr_pages') or []
                if _imgs_pdf and _pages_pdf and len(_imgs_pdf) == len(_pages_pdf):
                    from image_review_page import build_annotated_pages_for_pdf
                    from pdf_report import build_image_pdf_report
                    _ann = build_annotated_pages_for_pdf(
                        fb, _imgs_pdf, _pages_pdf,
                        ocr_layout_pages=st.session_state.get('ocr_layout_pages'))
                    if _ann:
                        _cfg_pdf['total_max'] = max_total
                        _pdf_bytes = build_image_pdf_report(
                            _ann, fb=fb, name=name, exam_level_cfg=_cfg_pdf,
                            genre=_asgn_pdf.get('genre', ''),
                            prompt_title=_prompt_title)
            except Exception:
                _pdf_bytes = None            # 图文版任何失败都静默退回文字版
            st.session_state[_pdf_key] = _pdf_bytes or build_pdf_report(
                fb=fb, name=name, exam_level_cfg=_cfg_pdf,
                genre=_asgn_pdf.get('genre', ''),
                prompt_title=_prompt_title,
            )
        from datetime import datetime as _dt_pdf
        st.download_button(
            "📄 下载学习报告 PDF（可保存 / 打印 / 转发给爸爸妈妈）",
            data=st.session_state[_pdf_key],
            file_name=f"华文通学习报告_{name}_{_dt_pdf.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            key="dl_pdf_report",
        )
    except Exception:
        pass  # PDF 导出失败不影响批改结果展示

    # ══════════════════════════════════════════════════════════
    # 模块 6:再提交按钮
    # ══════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📝 提交另一篇作文", key="resubmit_bottom"):
        _reset_for_new_essay()
        st.rerun()

