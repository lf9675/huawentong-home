import streamlit as st

st.set_page_config(
    page_title="CLever · 华文通 — 新加坡中学华文作文 AI 批改",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import urllib.parse as _uparse

WHATSAPP_NUMBER = "6594846916"   # 例: 6591234567(国家码+号码,无加号无空格)
CALIB_RATE = "80%"              # 例: 85%

# 预填消息:家长点开 WhatsApp 就是这句话,按一下发送即可,一个字不用打
_WA_MSG = {
    "zh": "您好！我想为孩子领取【华文通·改】的免费内测码。",
    "en": "Hi! I'd like a free beta code for CLever (华文通·改) for my child.",
}

# ══════════════════════════════════════════════════════════
# 双语落地页(2026-07-05)
# 受众:英文为主的新加坡家庭 + 华文较弱孩子的新移民家长 → 中/EN 一键切换
# 页面唯一任务:让家长联系获取内测码
# 发布前请全局搜索【请替换】占位符:WhatsApp 链接、校准命中率
# ══════════════════════════════════════════════════════════

# ── 全局样式 ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;600&display=swap');

* { font-family: 'Noto Sans SC', sans-serif; }
h1, h2, h3, h4 { font-family: 'Noto Serif SC', serif; }

[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
section[data-testid="stSidebarUserContent"] { display: none; }

.main { background: #faf8f5; }
.block-container { padding-top: 3.5rem; padding-bottom: 2rem; max-width: 1200px; }
header[data-testid="stHeader"] { background: transparent; }
.stApp > header { background: transparent; }

/* ── 顶部品牌栏 ── */
.top-bar {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-radius: 12px; padding: 0.9rem 1.5rem; margin-bottom: 1rem;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.brand { color: #f0c27f; font-family: 'Noto Serif SC', serif; font-size: 1.15rem; font-weight: 700; }
.brand-sub { color: #b8c5d6; font-size: 0.8rem; margin-left: 0.5rem; }

.nav-button-row .stButton > button {
    background: transparent; color: white;
    border: 1px solid rgba(240,194,127,0.4); border-radius: 8px;
    padding: 0.4rem 1rem; font-size: 0.9rem; font-weight: 500;
    width: 100%; height: 40px; transition: all 0.2s;
}
.nav-button-row .stButton > button:hover {
    background: rgba(240,194,127,0.15); border-color: #f0c27f;
    color: #f0c27f; transform: none; box-shadow: none;
}

/* ── 英雄区 ── */
.hero-h1 {
    font-family: 'Noto Serif SC', serif; font-size: 2.1rem; font-weight: 700;
    color: #1a1a2e; line-height: 1.35; margin: 0.5rem 0 0.8rem;
}
.hero-h1 .gold { color: #b8860b; }
.hero-sub { color: #555; font-size: 1.02rem; line-height: 1.8; margin-bottom: 1.2rem; }
.hero-cta {
    display: inline-block; background: linear-gradient(135deg, #0f3460, #16213e);
    color: #fff !important; text-decoration: none; border-radius: 10px;
    padding: 0.75rem 1.8rem; font-size: 1rem; font-weight: 600;
    box-shadow: 0 6px 18px rgba(15,52,96,0.25);
}
.hero-cta:hover { transform: translateY(-2px); }
.hero-cta-sub { color: #888; font-size: 0.82rem; margin-top: 0.5rem; }

/* ── 签名元素:批改实物演示卡 ── */
.demo-card {
    background: #fff; border: 1px solid #e8e0d5; border-radius: 14px;
    padding: 1.2rem 1.3rem; box-shadow: 0 10px 30px rgba(26,26,46,0.08);
    font-size: 0.88rem; line-height: 1.9;
}
.demo-head { font-size: 0.75rem; color: #888; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.demo-orig {
    background: #f5f4f0; border-left: 3px solid #ccc; border-radius: 5px;
    padding: 0.5rem 0.8rem; color: #666; margin-bottom: 0.55rem;
}
.demo-issue {
    background: #fdf8ee; border-left: 3px solid #f0c27f; border-radius: 5px;
    padding: 0.5rem 0.8rem; color: #5d3700; margin-bottom: 0.55rem; font-size: 0.84rem;
}
.demo-rev {
    background: #fdecea; border-left: 3px solid #c62828; border-radius: 5px;
    padding: 0.55rem 0.8rem; color: #2c2c2a;
}
.tag { font-weight: 700; font-size: 0.72rem; padding: 0 2px; }
.t-red { color: #c62828; } .t-orange { color: #ef6c00; }
.t-green { color: #2e7d32; } .t-blue { color: #1565c0; } .t-purple { color: #6a1b9a; }
.demo-delta {
    display: inline-block; background: #e8f5e9; color: #2e7d32;
    border-radius: 20px; padding: 0.15rem 0.8rem; font-weight: 700;
    font-size: 0.82rem; margin-top: 0.7rem;
}

/* ── 价值主张卡 ── */
.value-card {
    background: #fff; border: 1px solid #e8e0d5; border-radius: 14px;
    padding: 1.4rem 1.5rem; height: 100%;
}
.value-eyebrow { font-size: 0.72rem; letter-spacing: 0.12em; color: #b8860b; font-weight: 600; }
.value-title { font-family: 'Noto Serif SC', serif; font-size: 1.12rem; font-weight: 700;
    color: #1a1a2e; margin: 0.3rem 0 0.5rem; }
.value-body { color: #555; font-size: 0.9rem; line-height: 1.85; }

/* ── 流程步骤(真实时序,编号有信息量) ── */
.step-row { display: flex; gap: 0.9rem; align-items: flex-start; margin-bottom: 0.9rem; }
.step-num {
    flex: 0 0 34px; height: 34px; border-radius: 50%;
    background: #1a1a2e; color: #f0c27f; font-weight: 700;
    display: flex; align-items: center; justify-content: center; font-size: 0.9rem;
}
.step-text { color: #444; font-size: 0.92rem; line-height: 1.75; padding-top: 0.3rem; }
.step-text strong { color: #1a1a2e; }

/* ── 内测名额条 ── */
.beta-strip {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-radius: 14px; padding: 1.5rem 2rem; color: #fff; margin: 0.5rem 0 1rem;
}
.beta-strip h3 { color: #f0c27f; margin: 0 0 0.5rem; font-size: 1.25rem; }
.beta-strip p { color: #d5dce8; font-size: 0.92rem; line-height: 1.8; margin: 0; }

/* ── 章节标题 ── */
.sec-title {
    font-family: 'Noto Serif SC', serif; font-size: 1.4rem; font-weight: 700;
    color: #1a1a2e; margin: 1.8rem 0 1rem; text-align: center;
}

/* ── 页脚 ── */
.footer { text-align: center; color: #999; font-size: 0.8rem; margin-top: 2.5rem;
    padding-top: 1.2rem; border-top: 1px solid #e8e0d5; line-height: 2; }
.footer a { color: #0f3460; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 顶部品牌栏 + 导航
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="top-bar">
    <div>
        <span class="brand">CLever · 华文通</span>
        <span class="brand-sub">AI 华文学习平台 · 新加坡 SEAB 评分标准</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="nav-button-row">', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    st.button("🏠 首页", key="nav_home", disabled=True)
with nav_col2:
    if st.button("🎓 学生作文提交", key="nav_student"):
        st.switch_page("pages/student.py")
with nav_col3:
    if st.button("👩‍🏫 教师管理后台", key="nav_admin"):
        st.switch_page("pages/admin.py")
with nav_col4:
    if st.button("📈 学生进步追踪", key="nav_progress"):
        st.switch_page("pages/progress.py")
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 语言切换
# ══════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"
_, lc = st.columns([5, 1])
with lc:
    _lang_pick = st.radio("Language", ["中文", "EN"], horizontal=True,
                          label_visibility="collapsed",
                          index=0 if st.session_state["lang"] == "zh" else 1,
                          key="lang_radio")
st.session_state["lang"] = "zh" if _lang_pick == "中文" else "en"
L = st.session_state["lang"]
WHATSAPP_LINK = (f"https://wa.me/{WHATSAPP_NUMBER}"
                 f"?text={_uparse.quote(_WA_MSG[L])}")

# ══════════════════════════════════════════════════════════
# 文案(zh / en)
# ══════════════════════════════════════════════════════════
T = {
"zh": {
    "hero_h1": '每一篇作文,都值得一次<span class="gold">讲得明白</span>的批改',
    "hero_sub": ("为新加坡中学华文 / 高级华文学生打造的 AI 作文批改。"
                 "按考评局(SEAB)官方评分标准逐段批改,不只告诉孩子哪里错了,"
                 "更讲清楚<strong>为什么要改、怎么改</strong>——改完重交,亲眼看到分数变化。"),
    "cta": "WhatsApp 联系,领取免费内测码",
    "cta_sub": "8 月免费内测 · 仅 20 个名额 · 无需注册,不收集任何个人信息",
    "demo_head": "真实批改示范 · 议论文分论点段",
    "demo_orig": "学生原文:其次,学校应该举办各种阅读活动。例如,老师们可以推荐好书。",
    "demo_issue": "💡 提出观点后直接举例,少了「解释」——为什么举办活动就能培养阅读习惯?先讲道理,例子才有说服力。",
    "demo_rev": ('<span class="tag t-red">论点</span>学校应主动举办阅读活动。'
                 '<span class="tag t-orange">解释</span>活动能把阅读从一个人的事变成大家一起做的事。'
                 '<span class="tag t-green">举例</span>例如班级读书会、每周好书推荐。'
                 '<span class="tag t-blue">分析</span>学生听到别人聊书,自己也想读。'
                 '<span class="tag t-purple">扣题</span>这正是培养阅读风气的重要一步。'),
    "demo_delta": "🔁 修改后重交:比上一版 +4 分(35 → 39)",
    "v1_eye": "评分标准", "v1_title": "按 SEAB 官方标准给分,不凭感觉",
    "v1_body": (f"评分引擎逐条对照考评局官方评分指引,给出内容分、语文分和 O 水准等级预估;"
                f"并经资深华文教师用真实教师评分逐篇校准,±3 分内命中率 {CALIB_RATE}。"
                f"孩子在家练的,就是考场上那把尺。"),
    "v2_eye": "教学方法", "v2_title": "教育而非指令:先讲为什么,再讲怎么改",
    "v2_body": ("方法论来自近三十年新加坡中学华文与高级华文一线教学经验——记叙文四技法、"
                "议论文 PEEL 框架。每段给出提升版和高分版两层示范,每个句子标注它在段落里的作用,"
                "还配中英文语音讲解。孩子学到的是方法,不是答案。"),
    "v3_eye": "看得见的进步", "v3_title": "改了再交,进步用分数说话",
    "v3_body": ("每个访问码可批改 5 篇不同作文;每篇批改后,孩子按建议修改再交,"
                "系统自动对比上一版:「比上一版 +4 分」。一键导出 PDF 学习报告,"
                "家长不懂华文,也看得懂孩子的进步。"),
    "how_title": "怎么用?四步,三十秒出结果",
    "steps": [
        "<strong>提交作文</strong> — 手写作文拍照上传(AI 识别手写字),或直接打字粘贴。",
        "<strong>30 秒批改</strong> — 逐段诊断 + 一眼看到「最影响分数的一个问题」。",
        "<strong>看懂为什么</strong> — 每段两层修改示范、句子作用标注、中英文语音讲解。",
        "<strong>修改重交</strong> — 按建议改完再交,系统告诉孩子比上一版进步了多少。",
    ],
    "beta_h": "🎁 8 月免费内测 · 仅开放 20 个名额",
    "beta_p": ("每个内测码含 <strong>5 篇不同作文</strong>的批改额度,每篇可修改后重交"
               "(合计不超过 8 次),有效期 60 天,全程免费。适合中三、中四及高级华文学生,"
               "备考 O 水准会考。名额发完即止。"),
    "faq_title": "家长常见问题",
    "faqs": [
        ("需要提供孩子的姓名或学校吗?",
         "不需要。系统零个人信息设计:不收姓名、学校、电话、邮箱。孩子用访问码登录,"
         "挑一个系统生成的昵称(如「开朗的雨燕」),所有记录只跟着访问码走。"),
        ("孩子的作文数据安全吗?",
         "作文照片只用于文字识别,识别后立即丢弃,不存储。作文文字经匿名化后由第三方 AI"
         " 服务处理(详见隐私说明)。家长可随时凭访问码要求删除全部记录。"),
        ("AI 打的分数可靠吗?",
         f"评分逐条对照 SEAB 官方评分指引,并经资深教师用真实教师评分校准(±3 分内命中率 {CALIB_RATE})。"
         "AI 分数用于练习定位,不等同于会考成绩。"),
        ("适合哪些学生?",
         "中学华文和高级华文学生,尤其是中三、中四备考阶段。记叙文、议论文(含材料作文)都支持。"),
    ],
    "privacy_link": "📄 隐私与数据保护说明(PDPA)",
    "footer": ("CLever · 华文通 — 由拥有近三十年新加坡中学华文教学经验的资深教师打造<br>"
               "内测期免费 · 不收集个人信息 · "),
},
"en": {
    "hero_h1": 'Essay marking that actually <span class="gold">explains why</span>',
    "hero_sub": ("AI composition marking for Singapore Secondary Chinese / Higher Chinese students. "
                 "Paragraph-by-paragraph feedback against the official SEAB marking standards — "
                 "your child doesn't just see what's wrong, but <strong>why it matters and how to fix it</strong>. "
                 "Revise, resubmit, and watch the score improve."),
    "cta": "WhatsApp us for a free beta code",
    "cta_sub": "Free beta in August · 20 slots only · No sign-up, no personal data collected",
    "demo_head": "Real marking sample · Argumentative body paragraph",
    "demo_orig": "Student's original: 其次,学校应该举办各种阅读活动。例如,老师们可以推荐好书。",
    "demo_issue": "💡 The point jumps straight to an example — the 'Explain' step is missing. Why would activities build a reading habit? Reason first, then the example persuades.",
    "demo_rev": ('<span class="tag t-red">Point</span>学校应主动举办阅读活动。'
                 '<span class="tag t-orange">Explain</span>活动能把阅读从一个人的事变成大家一起做的事。'
                 '<span class="tag t-green">Example</span>例如班级读书会、每周好书推荐。'
                 '<span class="tag t-blue">Analyse</span>学生听到别人聊书,自己也想读。'
                 '<span class="tag t-purple">Link</span>这正是培养阅读风气的重要一步。'),
    "demo_delta": "🔁 Resubmitted after revision: +4 marks (35 → 39)",
    "v1_eye": "MARKING STANDARD", "v1_title": "Scored against official SEAB standards",
    "v1_body": (f"The marking engine follows the SEAB marking guidelines line by line — content marks, "
                f"language marks, and an O-Level grade estimate. Calibrated essay-by-essay against real "
                f"teacher scores by a veteran Chinese teacher: {CALIB_RATE} of scores land within ±3 marks. "
                f"Practice at home with the same yardstick used in the exam hall."),
    "v2_eye": "TEACHING METHOD", "v2_title": "Education, not instructions: why before how",
    "v2_body": ("The methodology comes from nearly 30 years of classroom experience teaching Secondary "
                "Chinese and Higher Chinese in Singapore — narrative techniques and the PEEL framework for "
                "argumentative writing. Every paragraph gets two model rewrites, each sentence tagged with "
                "its role, plus audio explanations in Mandarin and English."),
    "v3_eye": "VISIBLE PROGRESS", "v3_title": "Revise, resubmit, and see the score move",
    "v3_body": ("Each access code covers 5 different essays; after each marking, your child can revise and "
                "resubmit, and the system compares versions automatically: '+4 marks since your last draft'. "
                "One-click PDF learning reports — even if you don't read Chinese, you can see the progress."),
    "how_title": "How it works — four steps, results in 30 seconds",
    "steps": [
        "<strong>Submit</strong> — snap a photo of the handwritten essay (AI reads handwriting), or paste typed text.",
        "<strong>Marked in ~30s</strong> — paragraph-level diagnosis, plus the one issue costing the most marks.",
        "<strong>Understand why</strong> — two tiers of model rewrites, sentence-role tags, audio in Mandarin & English.",
        "<strong>Revise & resubmit</strong> — the system tells your child exactly how much the revision improved.",
    ],
    "beta_h": "🎁 Free August beta · 20 slots only",
    "beta_p": ("Each beta code includes marking for <strong>5 different essays</strong>, each revisable and "
               "resubmittable (8 submissions in total), valid 60 days, completely free. Best for Sec 3/4 and "
               "Higher Chinese students preparing for O-Levels. First come, first served."),
    "faq_title": "Frequently asked questions",
    "faqs": [
        ("Do I need to provide my child's name or school?",
         "No. The system is zero-PII by design: no names, schools, phone numbers or emails. Your child logs "
         "in with an access code and picks a system-generated nickname; all records follow the code only."),
        ("Is my child's essay data safe?",
         "Essay photos are used only for text recognition and discarded immediately — never stored. "
         "Anonymised essay text is processed by third-party AI services (see our privacy page). "
         "You can request full deletion at any time by quoting the access code."),
        ("Are the AI scores reliable?",
         f"Marking follows the official SEAB guidelines and is calibrated against real teacher scores "
         f"({CALIB_RATE} within ±3 marks). AI scores are for practice benchmarking, not official results."),
        ("Who is this for?",
         "Secondary Chinese and Higher Chinese students, especially Sec 3/4 exam preparation. "
         "Narrative and argumentative essays (including 材料作文) are both supported."),
    ],
    "privacy_link": "📄 Privacy & Data Protection (PDPA)",
    "footer": ("CLever · 华文通 — built by a veteran teacher with nearly 30 years of Singapore secondary "
               "Chinese teaching experience<br>Free during beta · No personal data collected · "),
},
}[L]

# ══════════════════════════════════════════════════════════
# 英雄区:左文案 + 右批改实物演示
# ══════════════════════════════════════════════════════════
hl, hr = st.columns([1.05, 1], gap="large")
with hl:
    st.markdown(f'<div class="hero-h1">{T["hero_h1"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">{T["hero_sub"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<a class="hero-cta" href="{WHATSAPP_LINK}" target="_blank">{T["cta"]}</a>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="hero-cta-sub">{T["cta_sub"]}</div>', unsafe_allow_html=True)
with hr:
    st.markdown(f"""
    <div class="demo-card">
        <div class="demo-head">{T["demo_head"]}</div>
        <div class="demo-orig">{T["demo_orig"]}</div>
        <div class="demo-issue">{T["demo_issue"]}</div>
        <div class="demo-rev">{T["demo_rev"]}</div>
        <div class="demo-delta">{T["demo_delta"]}</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 三个价值主张
# ══════════════════════════════════════════════════════════
st.markdown('<div style="height:1.2rem;"></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3, gap="medium")
for col, (eye, ttl, body) in zip(
        (c1, c2, c3),
        [(T["v1_eye"], T["v1_title"], T["v1_body"]),
         (T["v2_eye"], T["v2_title"], T["v2_body"]),
         (T["v3_eye"], T["v3_title"], T["v3_body"])]):
    with col:
        st.markdown(f"""
        <div class="value-card">
            <div class="value-eyebrow">{eye}</div>
            <div class="value-title">{ttl}</div>
            <div class="value-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 流程四步
# ══════════════════════════════════════════════════════════
st.markdown(f'<div class="sec-title">{T["how_title"]}</div>', unsafe_allow_html=True)
sc1, sc2 = st.columns(2, gap="large")
for i, step in enumerate(T["steps"]):
    with (sc1 if i < 2 else sc2):
        st.markdown(f"""
        <div class="step-row">
            <div class="step-num">{i + 1}</div>
            <div class="step-text">{step}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 内测名额条 + CTA
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="beta-strip">
    <h3>{T["beta_h"]}</h3>
    <p>{T["beta_p"]}</p>
</div>
""", unsafe_allow_html=True)
st.markdown(
    f'<div style="text-align:center;margin-bottom:0.5rem;">'
    f'<a class="hero-cta" href="{WHATSAPP_LINK}" target="_blank">{T["cta"]}</a></div>',
    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# FAQ
# ══════════════════════════════════════════════════════════
st.markdown(f'<div class="sec-title">{T["faq_title"]}</div>', unsafe_allow_html=True)
for q, a in T["faqs"]:
    with st.expander(q):
        st.markdown(a)

# ══════════════════════════════════════════════════════════
# 隐私链接 + 页脚
# ══════════════════════════════════════════════════════════
st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)
_, pc, _ = st.columns([2, 2, 2])
with pc:
    if st.button(T["privacy_link"], key="privacy_btn", use_container_width=True):
        st.switch_page("pages/privacy.py")

st.markdown(f'<div class="footer">{T["footer"]}© 2026 CLever · 华文通</div>',
            unsafe_allow_html=True)

