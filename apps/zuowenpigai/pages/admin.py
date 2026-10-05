import streamlit as st
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import (save_assignment, get_all_assignments, toggle_assignment,
                      delete_assignment, get_all_submissions)

st.set_page_config(page_title="教师管理后台", page_icon="👩‍🏫", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500&display=swap');
* { font-family: 'Noto Sans SC', sans-serif; }
h1,h2,h3,h4 { font-family: 'Noto Serif SC', serif; }
.main { background: #f5f7fa; }
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
    border: 1px solid #e0e7ef; margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.card h3 { color: #1a1a2e; font-family: 'Noto Serif SC', serif; margin-bottom: 1rem; }

.stat-box {
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    border-radius: 12px; padding: 1.2rem; text-align: center; color: white;
}
.stat-num { font-size: 2.5rem; font-weight: 700; color: #f0c27f; }
.stat-label { color: #b8c5d6; font-size: 0.85rem; }

.focus-box {
    background: #f0f7ff; border: 1px solid #b3d4ff; border-radius: 12px;
    padding: 1rem 1.2rem; margin: 0.8rem 0;
}
.focus-box h4 { color: #0f3460; margin-bottom: 0.6rem; font-size: 0.95rem; }
.focus-tag {
    display: inline-block; background: #0f3460; color: white;
    border-radius: 20px; padding: 0.2rem 0.7rem; font-size: 0.78rem;
    margin: 0.2rem;
}

.active-badge { background: #e8f5e9; color: #2e7d32; border-radius: 4px; padding: 0.2rem 0.6rem; font-size: 0.78rem; font-weight: 600; }
.inactive-badge { background: #fce4ec; color: #c62828; border-radius: 4px; padding: 0.2rem 0.6rem; font-size: 0.78rem; font-weight: 600; }
.viewed-tag { background: #e8f5e9; color: #2e7d32; border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.75rem; }
.not-viewed-tag { background: #fff3e0; color: #e65100; border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.75rem; }

.radar-label { font-size: 0.78rem; color: #666; }

.level-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 0.5rem; }
.level-table th { background: #1a1a2e; color: #f0c27f; padding: 0.5rem 0.8rem; text-align: left; }
.level-table td { padding: 0.5rem 0.8rem; border-bottom: 1px solid #e0e7ef; vertical-align: top; }
.level-table tr:nth-child(even) td { background: #f8fafc; }
.orig-cell { color: #c62828; }
.mid-cell { color: #e65100; }
.best-cell { color: #2e7d32; font-weight: 500; }
.tip-cell { color: #6a1b9a; font-size: 0.78rem; }

.stButton > button {
    background: linear-gradient(135deg, #0f3460, #16213e);
    color: white; border: none; border-radius: 10px;
    padding: 0.6rem 1.5rem; font-family: 'Noto Sans SC', sans-serif;
    font-size: 0.95rem; width: 100%;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(15,52,96,0.25); }
.stTextInput > div > div > input,
.stTextArea > div > div > textarea { border-radius: 10px; border-color: #e0e7ef; }
</style>
""", unsafe_allow_html=True)

# ── Password gate ──────────────────────────────────────────
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "teacher2024")
if 'admin_auth' not in st.session_state:
    st.session_state['admin_auth'] = False

if not st.session_state['admin_auth']:
    st.markdown("""
    <div class="page-header">
        <span style="font-size:2rem">👩‍🏫</span>
        <div><h2>教师管理后台</h2><p>请输入教师密码</p></div>
    </div>""", unsafe_allow_html=True)
    pw = st.text_input("教师密码", type="password")
    if st.button("登入"):
        if pw == ADMIN_PASSWORD:
            st.session_state['admin_auth'] = True
            st.rerun()
        else:
            st.error("密码错误，请重试。")
    st.stop()

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
            教师管理后台
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 横向导航按钮 ──
st.markdown("""<style>
.nav-row .stButton > button {
    background: transparent; color: #1a1a2e; border: 1px solid #e0e7ef;
    border-radius: 8px; padding: 0.4rem 1rem; font-size: 0.9rem;
    font-weight: 500; width: 100%; height: 40px; transition: all 0.2s;
}
.nav-row .stButton > button:hover {
    background: #f0f7ff; border-color: #1e88e5; color: #0f3460;
    transform: none; box-shadow: none;
}
</style><div class="nav-row">""", unsafe_allow_html=True)
nav1, nav2, nav3, nav4, nav5 = st.columns(5)
with nav1:
    if st.button("🏠 首页", key="nav_home_a"):
        st.switch_page("app.py")
with nav2:
    if st.button("🎓 学生作文提交", key="nav_student_a"):
        st.switch_page("pages/student.py")
with nav3:
    st.button("👩‍🏫 教师管理后台", key="nav_admin_a", disabled=True)
with nav4:
    if st.button("📈 学生进步追踪", key="nav_progress_a"):
        st.switch_page("pages/progress.py")
with nav5:
    if st.button("🚪 登出", key="nav_logout_a"):
        st.session_state['admin_auth'] = False
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Stats ───────────────────────────────────────────────────
all_assignments = get_all_assignments()
all_submissions = get_all_submissions()
active_count = sum(1 for a in all_assignments if a['is_active'])
viewed_count = sum(1 for s in all_submissions if s['viewed_at'])
unviewed_count = len(all_submissions) - viewed_count

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(all_assignments)}</div><div class="stat-label">作文题目总数</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{active_count}</div><div class="stat-label">开放中题目</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(all_submissions)}</div><div class="stat-label">学生提交总数</div></div>', unsafe_allow_html=True)
with c4:
    color = "#e53935" if unviewed_count > 0 else "#f0c27f"
    st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:{color}">{unviewed_count}</div><div class="stat-label">未查看批改</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 考试段定义（2026-07-11 起真正从 prompts.py 同步，单一来源）──
from prompts import EXAM_LEVELS as _PROMPT_LEVELS

EXAM_LEVELS_UI = {
    "HCL": "中学高级华文 (HCL) — 60分制",
    "PRACTICAL_HCL": "中学高级华文实用文 (HCL 1116) — 20分制",
    "O_CL": "中学普通华文 O水准 (CL 1160) — 40分制",
    "N_CL": "中学普通华文 N水准 (CL 1196) — 40分制",
    "PRACTICAL_O": "中学实用文 O水准 — 20分制",
    "PRACTICAL_N": "中学实用文 N水准 — 20分制",
}

# ── 文体选项（直接读 prompts.EXAM_LEVELS，杜绝两处清单再脱节）──
GENRES_BY_LEVEL = {k: list(v.get("genres") or ["记叙文"])
                   for k, v in _PROMPT_LEVELS.items()}

# ── All focus area options by genre ────────────────────────
FOCUS_OPTIONS = {
    "记叙文": [
        "错别字与基础病句",
        "人物描写（语言/动作/心理/外貌）",
        "情节结构（开头/发展/高潮/结局）",
        "感官细节与场景描写",
        "开头与结尾的呼应",
        "过渡句与段落连贯性",
        "主题与情感表达",
    ],
    "议论文": [
        "错别字与基础病句",
        "论点是否清晰",
        "论据是否充分有力",
        "论证逻辑（推理过程）",
        "段落结构（PEEL）",
        "开头的立场陈述",
        "结尾的总结升华",
    ],
    # 2026-07-11:"说明文"已从文体清单删除(易与事物类说明文混淆，新加坡学生不考)，
    # 此处对应的焦点选项一并移除，不再是死代码
    "材料议论文": [
        "错别字与基础病句",
        "是否紧扣材料（引用与转述）",
        "论点是否从材料中提炼",
        "论据是否在材料之外举出新例",
        "段落结构（PEEL）",
        "结尾是否回扣材料与升华",
    ],
    "演讲词": [
        "错别字与基础病句",
        "演讲格式（称呼/问候/结尾致谢按场合）",
        "听众意识与呼告语气",
        "论点是否清晰",
        "论证逻辑（推理过程）",
        "结尾的总结与号召力",
    ],
    "私人电邮": [
        "错别字与基础病句",
        "格式（称呼/问候语/结束语/署名）",
        "是否逐一回应来邮问题",
        "语气是否亲切得体",
        "分段与条理",
    ],
    "公务电邮": [
        "错别字与基础病句",
        "公务格式（主题/称呼/敬语/署名）",
        "开头是否交代身份与目的",
        "建议是否具体可行",
        "语气是否正式得体",
    ],
    "网上论坛": [
        "错别字与基础病句",
        "格式（称呼语/署名规则）",
        "是否回应帖中各方观点",
        "自己的立场与理由是否清楚",
        "语气是否切合网络语境",
    ],
    # 旧键保留：历史题目 genre="电子邮件" 仍能取到焦点清单
    "电子邮件": [
        "错别字与基础病句",
        "格式是否正确（称谓/日期/署名）",
        "语气是否得体",
        "内容是否切合情境",
        "分段与条理",
    ],
}

tab1, tab2, tab3 = st.tabs(["➕ 创建新题目", "📋 管理题目", "📊 学生提交记录"])

# ══════════════════════════════════════════════════════════
# TAB 1: Create Assignment
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="card"><h3>✏️ 创建新作文题目</h3>', unsafe_allow_html=True)

    # 第一行：考试段（最关键的选择，决定后续所有内容）
    exam_level = st.selectbox(
        "📚 考试段（决定评分标准）",
        list(EXAM_LEVELS_UI.keys()),
        format_func=lambda k: EXAM_LEVELS_UI[k],
        help="系统会自动套用对应的 SEAB 官方评分标准，无需手动输入 rubric"
    )

    # 显示当前考试段的官方信息
    level_info = {
        "HCL": ("60", "500", "内容(30) + 语文(30)"),
        "PRACTICAL_HCL": ("20", "220", "内容(10) + 语文(10)"),
        "O_CL": ("40", "300", "内容(20) + 语文(20)"),
        "N_CL": ("40", "240", "内容(20) + 语文(20)"),
        "PRACTICAL_O": ("20", "150", "内容(10) + 语文(10)"),
        "PRACTICAL_N": ("20", "120", "内容(10) + 语文(10)"),
    }
    total, min_words, breakdown = level_info[exam_level]
    st.info(f"📋 **{EXAM_LEVELS_UI[exam_level]}**　总分 **{total}**　字数要求 **{min_words}+ 字**　评分维度：{breakdown}")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("题目名称（供老师识别用）", placeholder="例如：HCL 期中考 1 - 论手机利弊")
    with col2:
        # 文体根据考试段动态变化
        available_genres = GENRES_BY_LEVEL.get(exam_level, ["记叙文"])
        genre = st.selectbox("文体", available_genres)

    prompt = st.text_area("写作题目（学生看到的）", placeholder="例如：《第一次独立旅行》\n请以此为题，写一篇记叙文……", height=90)
    requirements = st.text_area("写作要求（选填）", placeholder=f"例如：字数不少于{min_words}字；必须有清晰的起伏情节；运用至少两种描写手法", height=70)

    # rubric 改成"补充说明"，因为官方标准已经自动嵌入
    rubric = st.text_area(
        "📝 老师补充说明（选填，附加在 SEAB 官方标准之后）",
        placeholder="例如：本次特别看重学生是否能结合个人经历，举出真实例子。\n如不填，AI 将完全按 SEAB 官方标准评分。",
        height=80,
        help="官方 SEAB 评分标准已自动嵌入，老师只需补充本次教学的特别要求即可"
    )

    # ── Focus area toggles ──────────────────────────────────
    st.markdown('<div class="focus-box"><h4>🎯 本次批改焦点（勾选需要重点批改的项目）</h4>', unsafe_allow_html=True)
    st.caption("只勾选本次课程重点，减少学生认知负荷。全不勾选 = AI按官方标准全面批改。")

    focus_opts = FOCUS_OPTIONS.get(genre, FOCUS_OPTIONS["记叙文"])
    selected_focus = []
    cols = st.columns(2)
    for i, opt in enumerate(focus_opts):
        with cols[i % 2]:
            if st.checkbox(opt, key=f"focus_{i}"):
                selected_focus.append(opt)

    if selected_focus:
        tags = "".join([f'<span class="focus-tag">✓ {f}</span>' for f in selected_focus])
        st.markdown(f"<p style='margin-top:0.5rem;'>已选：{tags}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💾 保存题目"):
        if not title or not prompt:
            st.error("请填写题目名称和写作题目。")
        else:
            aid = save_assignment(title, exam_level, genre, prompt, requirements, rubric, selected_focus)
            st.success(f"✅ 题目已保存！系统已套用 {EXAM_LEVELS_UI[exam_level]} 的官方评分标准。学生现在可以提交作文了。")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2: Manage Assignments
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="card"><h3>📋 所有作文题目</h3>', unsafe_allow_html=True)
    if not all_assignments:
        st.info("还没有创建任何题目。")
    else:
        for a in all_assignments:
            badge = '<span class="active-badge">✅ 开放中</span>' if a['is_active'] else '<span class="inactive-badge">⏸ 已关闭</span>'
            sub_count = sum(1 for s in all_submissions if s['assignment_id'] == a['id'])
            with st.expander(f"📝 {a['title']} — {a['genre']}  {badge}  ({sub_count}份提交)", expanded=False):
                st.markdown(f"**题目：** {a['prompt']}")
                if a.get('requirements'):
                    st.markdown(f"**要求：** {a['requirements']}")

                # Show focus areas
                try:
                    focus_list = json.loads(a.get('focus_areas') or '[]')
                except:
                    focus_list = []
                if focus_list:
                    tags = "".join([f'<span class="focus-tag">✓ {f}</span>' for f in focus_list])
                    st.markdown(f"**批改焦点：** {tags}", unsafe_allow_html=True)
                else:
                    st.caption("批改焦点：全维度（未设定）")

                st.caption(f"创建时间：{a['created_at'][:16] if a['created_at'] else '—'}")
                col_a, col_b = st.columns(2)
                with col_a:
                    label = "⏸ 关闭题目" if a['is_active'] else "✅ 重新开放"
                    if st.button(label, key=f"toggle_{a['id']}"):
                        toggle_assignment(a['id'], 0 if a['is_active'] else 1)
                        st.rerun()
                with col_b:
                    if st.button("🗑️ 删除题目", key=f"del_{a['id']}"):
                        delete_assignment(a['id'])
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 3: Submissions
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="card"><h3>📊 学生提交记录</h3>', unsafe_allow_html=True)

    if not all_submissions:
        st.info("还没有学生提交作文。")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            assignment_filter_options = ["全部题目"] + list(dict.fromkeys(s['assignment_title'] for s in all_submissions))
            filter_choice = st.selectbox("筛选题目", assignment_filter_options)
        with col_f2:
            view_filter = st.radio("查看状态", ["全部", "未查看", "已查看"], horizontal=True)

        filtered = all_submissions if filter_choice == "全部题目" else [s for s in all_submissions if s['assignment_title'] == filter_choice]
        if view_filter == "未查看":
            filtered = [s for s in filtered if not s['viewed_at']]
        elif view_filter == "已查看":
            filtered = [s for s in filtered if s['viewed_at']]

        st.caption(f"显示 {len(filtered)} 份提交")

        # ── 2026-07-12:导出校准 CSV(AI 分数逐篇导出,老师在 Excel 补"人评分"列)──
        try:
            import csv as _csv
            import io as _io
            _buf = _io.StringIO()
            _w = _csv.writer(_buf)
            _w.writerow(["提交时间", "学生", "编号", "题目", "文体", "考级",
                         "AI内容分", "AI语文分", "AI总分", "AI等级",
                         "人评内容分", "人评语文分", "人评总分", "问题指得对吗(备注)"])
            for _s in filtered:
                _fb = {}
                try:
                    _fb = json.loads(_s.get('feedback_json') or '{}')
                except Exception:
                    pass
                _sc = _fb.get('scores') or {}
                _w.writerow([
                    (_s.get('submitted_at') or '')[:16],
                    _s.get('student_name') or '', _s.get('student_id') or '',
                    _s.get('assignment_title') or '',
                    _s.get('genre') or '', _s.get('exam_level') or '',
                    _sc.get('content', ''), _sc.get('language', ''),
                    _sc.get('total', ''), _fb.get('grade_estimate', ''),
                    '', '', '', '',
                ])
            st.download_button(
                "📥 导出校准 CSV（AI 分数 → Excel 补人评分）",
                data='\ufeff' + _buf.getvalue(),   # BOM:Excel 打开中文不乱码
                file_name="校准记录.csv", mime="text/csv",
                key="dl_calibration_csv")
        except Exception:
            pass  # 导出失败不影响列表

        # ══════════════════════════════════════════════════════
        # 2026-07-13 决策:校准报告生成器(信任机制③,刘老师裁定口径)
        #   作文评分本身主观,不同老师之间也有分差,不死磕分数吻合度。
        #   主指标 = 问题命中率(AI 指出的主要问题,老师是否认同);
        #   分数只看 同档/相邻档率 + 平均偏差;±3分率仅作参考。
        #   流程:上面导出 CSV → Excel 补人评分列 → 传回来自动出报告。
        # ══════════════════════════════════════════════════════
        with st.expander("📈 生成校准报告（上传已填人评分的校准CSV）", expanded=False):
            st.caption(
                "用法:先点上方按钮导出 CSV,在 Excel 里填好"
                "「人评内容分 / 人评语文分 / 人评总分 / 问题指得对吗(备注)」四列后传回来。"
                "「问题指得对吗」一栏:认同 AI 指出的主要问题就填「对」,"
                "不认同填「不对」,后面可以加备注文字。")
            _calib_up = st.file_uploader("上传已填好的校准 CSV",
                                         type=["csv"], key="calib_csv_up")
            if _calib_up is not None:
                try:
                    import csv as _csv3
                    import io as _io3
                    from prompts import estimate_grade_hcl, estimate_grade_cl

                    _text = _calib_up.getvalue().decode("utf-8-sig", errors="replace")
                    _rows = list(_csv3.DictReader(_io3.StringIO(_text)))

                    # ── 等级序:用于"同档/相邻档"判定;HCL 的 D7-F9 归入 D7 档位 ──
                    _ORDER = {"A1": 0, "A2": 1, "B3": 2, "B4": 3, "C5": 4,
                              "C6": 5, "D7": 6, "E8": 7, "F9": 8, "D7-F9": 6}

                    def _grade_of(total, level_str):
                        """按考级字符串推断等级换算口径(容错:认不出就按 CL 40 分制)"""
                        s = str(level_str or "")
                        if ("实用" in s) or ("PRACTICAL" in s.upper()):
                            return estimate_grade_cl(total, max_score=20)
                        if ("高级" in s) or ("HCL" in s.upper()):
                            return estimate_grade_hcl(total)
                        return estimate_grade_cl(total, max_score=40)

                    def _judge(remark):
                        """解析「问题指得对吗」列:返回 'yes' / 'no' / None(未填)"""
                        r = str(remark or "").strip()
                        if not r:
                            return None
                        if r[0] in "对是√✓yY1" or r.startswith("认同"):
                            return "yes"
                        if r[0] in "不否×xXnN0错":
                            return "no"
                        return None   # 只写了备注没给判定,不计入分母

                    n_scored = 0          # 填了人评总分的篇数
                    diffs = []            # AI总分 - 人评总分
                    band_pass = 0         # 同档或相邻档
                    band_total = 0
                    hit_yes, hit_no = 0, 0
                    outliers = []         # 需要重点复核的篇目

                    for _r in _rows:
                        # 问题命中(不依赖人评分数,单独统计)
                        _j = _judge(_r.get("问题指得对吗(备注)")
                                    or _r.get("问题指得对吗"))
                        if _j == "yes":
                            hit_yes += 1
                        elif _j == "no":
                            hit_no += 1

                        try:
                            _ai_t = int(float(_r.get("AI总分") or ""))
                            _hu_t = int(float(_r.get("人评总分") or ""))
                        except (ValueError, TypeError):
                            # 人评分没填的行:只参与问题命中统计,跳过分数统计
                            if _j == "no":
                                outliers.append((_r.get("学生", ""),
                                                 _r.get("题目", ""),
                                                 "老师不认同 AI 指的问题",
                                                 _r.get("问题指得对吗(备注)", "")))
                            continue

                        n_scored += 1
                        _d = _ai_t - _hu_t
                        diffs.append(_d)

                        _lv = _r.get("考级", "")
                        _g_ai = _grade_of(_ai_t, _lv)
                        _g_hu = _grade_of(_hu_t, _lv)
                        if _g_ai in _ORDER and _g_hu in _ORDER:
                            band_total += 1
                            if abs(_ORDER[_g_ai] - _ORDER[_g_hu]) <= 1:
                                band_pass += 1

                        # 复核清单:分差过大 或 问题被老师否定
                        if abs(_d) > 5 or _j == "no":
                            _why = []
                            if abs(_d) > 5:
                                _why.append(f"分差 {_d:+d}(AI {_ai_t} / 人评 {_hu_t})")
                            if _j == "no":
                                _why.append("老师不认同 AI 指的问题")
                            outliers.append((_r.get("学生", ""),
                                             _r.get("题目", ""),
                                             ";".join(_why),
                                             _r.get("问题指得对吗(备注)", "")))

                    hit_total = hit_yes + hit_no
                    if hit_total == 0 and n_scored == 0:
                        st.warning("CSV 里没有找到已填写的人评分或「问题指得对吗」判定,"
                                   "请确认列名与导出模板一致、且至少填了一行。")
                    else:
                        # ── 指标卡(问题命中率放第一位 = 主指标)──
                        _c1, _c2, _c3, _c4 = st.columns(4)
                        _hit_rate = (f"{hit_yes / hit_total * 100:.0f}%"
                                     if hit_total else "—")
                        _band_rate = (f"{band_pass / band_total * 100:.0f}%"
                                      if band_total else "—")
                        _avg_dev = (f"{sum(abs(d) for d in diffs) / len(diffs):.1f} 分"
                                    if diffs else "—")
                        _in3_rate = (f"{sum(1 for d in diffs if abs(d) <= 3) / len(diffs) * 100:.0f}%"
                                     if diffs else "—")
                        _c1.metric("⭐ 问题命中率(主指标)", _hit_rate,
                                   help=f"老师认同 AI 指出的主要问题:{hit_yes}/{hit_total} 篇")
                        _c2.metric("同档或相邻档率", _band_rate,
                                   help=f"AI 与人评落在同一或相邻等级:{band_pass}/{band_total} 篇")
                        _c3.metric("平均分差(绝对值)", _avg_dev)
                        _c4.metric("±3分率(仅参考)", _in3_rate)

                        # ── 需重点复核的篇目 ──
                        if outliers:
                            st.markdown("**🔍 建议重点复核的篇目**")
                            for _o in outliers:
                                st.markdown(f"- **{_o[0]}**《{_o[1]}》— {_o[2]}"
                                            + (f"（老师备注:{_o[3]}）" if _o[3] else ""))

                        # ── 可分享的校准报告(Markdown 下载)──
                        _rpt = (
                            f"# 华文通·改 校准报告\n\n"
                            f"- 校准样本:{max(n_scored, hit_total)} 篇"
                            f"(人评分 {n_scored} 篇;问题判定 {hit_total} 篇)\n"
                            f"- **问题命中率:{_hit_rate}**"
                            f"(老师认同 AI 指出的主要问题 {hit_yes}/{hit_total} 篇)\n"
                            f"- 等级判断:同档或相邻档 {_band_rate}"
                            f"({band_pass}/{band_total} 篇)\n"
                            f"- 平均分差:{_avg_dev}(±3 分内 {_in3_rate},仅供参考)\n\n"
                            f"> 说明:作文评分带有主观性,不同老师之间本身存在分差。"
                            f"本平台的校准以「AI 抓问题的眼光是否与资深老师一致」为主要标准,"
                            f"等级判断以「不跨档」为底线。\n"
                        )
                        st.download_button("📄 下载校准报告(可分享给内测老师)",
                                           data=_rpt, file_name="校准报告.md",
                                           mime="text/markdown",
                                           key="dl_calib_report")
                except Exception as _e:
                    st.error(f"校准报告生成失败:{_e}")

        for sub in filtered:
            # 2026-07-12 修复:st.expander 标题不支持 HTML,旧的 <span> 原样漏出;改纯文字
            viewed_html = '✅ 已查看' if sub['viewed_at'] else '⚠️ 未查看'
            submitted_time = sub['submitted_at'][:16] if sub['submitted_at'] else '—'

            with st.expander(f"👤 {sub['student_name']} ({sub['student_id']})  —  {sub['assignment_title']}  {viewed_html}  {submitted_time}", expanded=False):

                col_img, col_fb = st.columns([1, 2])

                with col_img:
                    if sub.get('image_data'):
                        # 2026-08-06 决策：streamlit 1.61.0 移除了已废弃的 use_column_width，
                        #   改用 use_container_width（行为等价）。
                        st.image(sub['image_data'], caption="学生作文原图",
                                 use_container_width=True)
                    if sub.get('ocr_text'):
                        with st.expander("📄 OCR识别文字"):
                            st.text(sub['ocr_text'])

                with col_fb:
                    if sub.get('feedback_json'):
                        try:
                            fb = json.loads(sub['feedback_json'])
                        except:
                            fb = {}

                        # Radar scores
                        scores = fb.get('scores', {})
                        if scores:
                            try:
                                import plotly.graph_objects as go
                                dims = list(scores.keys())
                                vals = list(scores.values())
                                vals_closed = vals + [vals[0]]
                                dims_closed = dims + [dims[0]]
                                fig = go.Figure(go.Scatterpolar(
                                    r=vals_closed, theta=dims_closed,
                                    fill='toself',
                                    fillcolor='rgba(15,52,96,0.15)',
                                    line=dict(color='#0f3460', width=2),
                                    marker=dict(size=6, color='#f0c27f')
                                ))
                                fig.update_layout(
                                    polar=dict(radialaxis=dict(visible=True, range=[0,10])),
                                    showlegend=False, height=280, margin=dict(l=30,r=30,t=30,b=30),
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            except:
                                pass

                        # Strengths
                        strengths = fb.get('strengths', [])
                        if strengths:
                            st.markdown("**✅ 优点**")
                            for s in strengths: st.markdown(f"- {s}")

                        # Upgrade table
                        upgrades = fb.get('upgrade_table', [])
                        if upgrades:
                            st.markdown("**⬆️ 升级改写**")
                            rows_html = ""
                            for u in upgrades:
                                rows_html += f"""<tr>
                                    <td class="orig-cell">{u.get('original','')}</td>
                                    <td class="mid-cell">{u.get('level2','')}</td>
                                    <td class="best-cell">{u.get('level3','')}</td>
                                    <td class="tip-cell">{u.get('tip','')}</td>
                                </tr>"""
                            st.markdown(f"""
                            <table class="level-table">
                                <tr><th>原句</th><th>及格版</th><th>优秀版 ⭐</th><th>升级秘籍</th></tr>
                                {rows_html}
                            </table>""", unsafe_allow_html=True)

                        overall = fb.get('overall_suggestion', '')
                        if overall:
                            st.markdown(f"**🎯 总建议：** {overall}")

                        viewed_time = sub['viewed_at'][:16] if sub['viewed_at'] else '尚未查看'
                        st.caption(f"查看批改时间：{viewed_time}")

    st.markdown('</div>', unsafe_allow_html=True)

