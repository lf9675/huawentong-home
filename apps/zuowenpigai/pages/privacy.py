import streamlit as st

st.set_page_config(page_title="隐私与数据保护 | CLever · 华文通",
                   page_icon="📄", layout="centered",
                   initial_sidebar_state="collapsed")

import urllib.parse as _uparse

WHATSAPP_NUMBER = "6594846916"   # 例: 6591234567
_PP_MSG = {
    "zh": "您好！我想咨询【华文通·改】的隐私/数据问题(如需删除数据,请附上访问码)。",
    "en": "Hi! I have a privacy/data question about CLever (华文通·改). "
          "For deletion requests, please include the access code.",
}

# ══════════════════════════════════════════════════════════
# 隐私与数据保护说明页(PDPA)— 2026-07-05
# 原则:如实披露,尤其是第三方 AI 处理与跨境传输;不做做不到的承诺。
# 本页为内测期版本;12 月注册 ACRA 实体后需更新"运营者"与"联系方式"。
# 发布前请全局搜索【请替换】占位符。
# ══════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;600&display=swap');
* { font-family: 'Noto Sans SC', sans-serif; }
h1, h2, h3 { font-family: 'Noto Serif SC', serif; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
.main { background: #faf8f5; }
.block-container { max-width: 820px; padding-top: 3rem; }
.pp-title { font-family:'Noto Serif SC',serif; font-size:1.7rem; font-weight:700;
    color:#1a1a2e; margin-bottom:0.2rem; }
.pp-date { color:#999; font-size:0.82rem; margin-bottom:1.2rem; }
.pp-sec { font-family:'Noto Serif SC',serif; font-size:1.12rem; font-weight:700;
    color:#0f3460; margin:1.5rem 0 0.5rem; }
.pp-body { color:#444; font-size:0.93rem; line-height:1.95; }
.pp-body strong { color:#1a1a2e; }
.pp-hl { background:#fdf8ee; border-left:3px solid #f0c27f; border-radius:6px;
    padding:0.7rem 1rem; margin:0.6rem 0; color:#5d3700; font-size:0.9rem; line-height:1.9; }
</style>
""", unsafe_allow_html=True)

# ── 语言切换 ──
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"
hc, lc = st.columns([4, 1])
with lc:
    _pick = st.radio("Language", ["中文", "EN"], horizontal=True,
                     label_visibility="collapsed",
                     index=0 if st.session_state["lang"] == "zh" else 1,
                     key="pp_lang_radio")
st.session_state["lang"] = "zh" if _pick == "中文" else "en"
WHATSAPP_LINK = (f"https://wa.me/{WHATSAPP_NUMBER}"
                 f"?text={_uparse.quote(_PP_MSG[st.session_state['lang']])}")

LAST_UPDATED = "2026-07-05"

if st.session_state["lang"] == "zh":
    st.markdown('<div class="pp-title">隐私与数据保护说明</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pp-date">依据新加坡《个人数据保护法》(PDPA 2012) · '
                f'最后更新:{LAST_UPDATED} · 内测期版本</div>', unsafe_allow_html=True)

    st.markdown("""
<div class="pp-body">
本说明介绍 <strong>CLever · 华文通</strong>(下称"本服务")在作文批改过程中如何处理数据。
本服务从产品设计之初就采用<strong>零个人信息(Zero-PII)架构</strong>:我们尽最大可能不收集、
不存储能识别孩子身份的信息。
</div>

<div class="pp-sec">一、我们不收集什么</div>
<div class="pp-body">
本服务<strong>不收集、不要求提供</strong>:学生姓名、学校名称、班级、学号、电话号码、
电子邮箱、住址、出生日期、照片中的人像。学生使用系统生成的昵称(如"开朗的雨燕"),
昵称与真实身份没有任何关联。
</div>

<div class="pp-sec">二、我们处理什么</div>
<div class="pp-body">
为完成批改,本服务处理以下数据:<br>
① <strong>作文内容</strong> — 学生提交的作文文字(打字输入,或由照片识别所得);<br>
② <strong>批改结果</strong> — 分数、等级预估、逐段反馈,与访问码关联,用于历史记录和进步对比;<br>
③ <strong>访问码</strong> — 系统只存储访问码的 SHA-256 加密哈希,<strong>不存储明文</strong>,
任何人(包括运营者)都无法从数据库反推出访问码本身;<br>
④ <strong>使用记录</strong> — 每次提交的时间与次数,用于额度管理。<br><br>
<strong>作文照片:</strong>手写作文的照片仅用于当次文字识别,识别完成后<strong>立即丢弃,
不写入数据库,不留存任何副本</strong>。
</div>

<div class="pp-sec">三、第三方处理与跨境传输(重要披露)</div>
<div class="pp-hl">
作文批改由第三方 AI 服务完成:文字识别使用智谱 GLM(Zhipu AI),批改使用 DeepSeek。
这两家服务商的服务器位于<strong>中国大陆</strong>。发送给它们的内容<strong>仅包含作文文字
与题目</strong>,不包含姓名、昵称、访问码或任何身份信息——服务商收到的是一篇无法追溯到
任何个人的匿名作文。上述服务商对所接收数据的处理受其各自隐私政策约束。
若您不接受此安排,请不要使用本服务。
</div>

<div class="pp-sec">四、数据保存与删除</div>
<div class="pp-body">
批改记录在访问码有效期内保存,供学生查看历史报告和对比进步;有效期结束后最长保留
6 个月,用于评分质量校验,之后删除。家长可<strong>随时</strong>凭访问码(或访问码的
任意一次提交记录)联系我们,要求立即删除该码名下的全部数据,我们将在 7 个工作日内完成
并确认。
</div>

<div class="pp-sec">五、未成年人</div>
<div class="pp-body">
本服务面向中学生,访问码由家长或监护人获取并转交孩子使用。家长获取并启用访问码,
即视为同意孩子按本说明使用本服务。我们建议家长陪同孩子完成首次使用。
</div>

<div class="pp-sec">六、安全措施</div>
<div class="pp-body">
全站 HTTPS 加密传输;访问码仅存哈希;数据库访问受凭证保护;不使用任何广告追踪或
第三方营销 Cookie;浏览器会话数据仅用于维持登录状态,关闭页面后失效。
</div>

<div class="pp-sec">七、本说明的更新</div>
<div class="pp-body">
本服务目前处于免费内测阶段。正式运营时(预计 2027 年初),本页将更新运营实体信息,
并在页面顶部标注变更日期。重大变更会在学生登录页提示。
</div>

<div class="pp-sec">八、联系我们</div>
<div class="pp-body">
数据删除请求、隐私相关疑问,请通过 WhatsApp 联系:
<a href="{WA}" target="_blank">点此联系</a>。
</div>
""".replace("{WA}", WHATSAPP_LINK), unsafe_allow_html=True)

else:
    st.markdown('<div class="pp-title">Privacy & Data Protection Notice</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="pp-date">In line with the Singapore Personal Data Protection '
                f'Act (PDPA 2012) · Last updated: {LAST_UPDATED} · Beta version</div>',
                unsafe_allow_html=True)

    st.markdown("""
<div class="pp-body">
This notice explains how <strong>CLever · 华文通</strong> ("the Service") handles data when
marking compositions. The Service is built on a <strong>zero-PII architecture</strong>:
we avoid collecting or storing anything that could identify your child.
</div>

<div class="pp-sec">1. What we do not collect</div>
<div class="pp-body">
The Service <strong>does not collect or request</strong>: student names, school names,
classes, student IDs, phone numbers, email addresses, home addresses, dates of birth,
or faces in photos. Students use a system-generated nickname (e.g. "开朗的雨燕") that has
no link to their real identity.
</div>

<div class="pp-sec">2. What we process</div>
<div class="pp-body">
To mark an essay, the Service processes:<br>
① <strong>Essay content</strong> — the text your child submits (typed, or recognised from a photo);<br>
② <strong>Marking results</strong> — scores, grade estimates and paragraph feedback, linked to the
access code for history and progress comparison;<br>
③ <strong>Access codes</strong> — only a SHA-256 hash is stored, <strong>never the plain code</strong>;
no one, including the operator, can recover a code from the database;<br>
④ <strong>Usage logs</strong> — submission timestamps and counts, for quota management.<br><br>
<strong>Essay photos:</strong> photos of handwritten essays are used only for one-time text
recognition and are <strong>discarded immediately — never written to the database, no copies kept</strong>.
</div>

<div class="pp-sec">3. Third-party processing & overseas transfer (important disclosure)</div>
<div class="pp-hl">
Marking is performed by third-party AI services: text recognition by Zhipu GLM and marking by
DeepSeek, whose servers are located in <strong>mainland China</strong>. Only the <strong>essay text
and the essay question</strong> are sent — no names, nicknames, access codes or any identifying
information. What these providers receive is an anonymous essay that cannot be traced to any
individual. Their handling of received data is governed by their respective privacy policies.
If you are not comfortable with this arrangement, please do not use the Service.
</div>

<div class="pp-sec">4. Retention & deletion</div>
<div class="pp-body">
Marking records are kept for the validity period of the access code, so students can review past
reports and track progress; after expiry they are retained for at most 6 months for marking-quality
verification, then deleted. Parents may <strong>at any time</strong> request immediate deletion of
all data under a code by contacting us and quoting the access code (or any submission under it).
We will complete and confirm deletion within 7 working days.
</div>

<div class="pp-sec">5. Children</div>
<div class="pp-body">
The Service is designed for secondary school students. Access codes are obtained by parents or
guardians and passed to the child. By obtaining and activating a code, the parent consents to the
child's use of the Service under this notice. We recommend parents accompany their child for the
first session.
</div>

<div class="pp-sec">6. Security</div>
<div class="pp-body">
All traffic is encrypted over HTTPS; access codes are stored as hashes only; database access is
credential-protected; no advertising trackers or third-party marketing cookies are used; browser
session data only maintains the login state and expires when the page is closed.
</div>

<div class="pp-sec">7. Changes to this notice</div>
<div class="pp-body">
The Service is currently in a free beta. When it launches commercially (expected early 2027),
this page will be updated with the operating entity's details, with the change date shown at the
top. Material changes will be announced on the student login page.
</div>

<div class="pp-sec">8. Contact</div>
<div class="pp-body">
For deletion requests or privacy questions, contact us on WhatsApp:
<a href="{WA}" target="_blank">tap to chat</a>.
</div>
""".replace("{WA}", WHATSAPP_LINK), unsafe_allow_html=True)

st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
if st.button("← 返回首页 / Back to home", key="pp_back"):
    st.switch_page("app.py")

