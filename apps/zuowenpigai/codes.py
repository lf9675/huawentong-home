"""
访问码管理页(老师端)— P1 #4
访问方式:应用网址后加 /codes,或从教师后台进入(如已加导航按钮)
2026-07-05 UX 修整:
- 应用链接存库,填一次永久记住
- 单码操作下拉框显示 昵称+用量+状态,不再是裸 ID
- 新增"重新启用"(修复停用不可撤销)
- 码列表新增"今日已用"列
- 使用记录改为常驻折叠区(原按钮态一闪即逝)
- 生成区补"我已保存,清除显示"按钮(与重发一致)
- 校准样本 tab 升级为校准记录表:内容/语文分拆列 + 分文体命中率 + CSV 导出
"""
import io
import csv
import streamlit as st

from access_codes import (init_access_tables, generate_codes, list_codes,
                          get_usage_log, deactivate_code, reactivate_code,
                          reissue_code, DAILY_LIMIT, list_calibration_samples,
                          get_setting, set_setting, today_usage_map)

st.set_page_config(page_title="访问码管理 | CLever · 华文通", page_icon="🔑", layout="wide")

# 隐藏侧栏(与 admin/progress 页一致)
st.markdown("""<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
</style>""", unsafe_allow_html=True)

st.markdown("## 🔑 访问码管理")

# ── 教师密码门(与 admin.py 相同模式)──────────────────────
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "teacher2024")
if not st.session_state.get("codes_auth"):
    pw = st.text_input("教师密码", type="password", key="codes_pw")
    if st.button("登录", key="codes_login"):
        if pw == ADMIN_PASSWORD:
            st.session_state["codes_auth"] = True
            st.rerun()
        else:
            st.error("密码错误")
    st.stop()

if ADMIN_PASSWORD == "teacher2024":
    st.warning("⚠️ 正在使用默认教师密码。内测发码前,请到 Streamlit Secrets 设置 ADMIN_PASSWORD。")

init_access_tables()

# ── 应用链接:存库,填一次永久记住(2026-07-05) ─────────────
_saved_link = get_setting("app_link", "")
app_link = st.text_input("应用链接(用于生成发码消息,自动记住)",
                         value=_saved_link,
                         placeholder="https://xxx.streamlit.app",
                         key="app_link_input")
if app_link.strip() != _saved_link:
    set_setting("app_link", app_link.strip())
    st.toast("应用链接已保存,下次登录不用重填。")


def build_parent_message(code, quota, expiry, link):
    link = link or "[应用链接]"
    return (f"您好！这是孩子的作文批改访问码：{code}（输入时横线也要打）。"
            f"打开 {link} 输入即可使用，共 {quota} 篇批改额度，每天最多 {DAILY_LIMIT} 篇，"
            f"有效期至 {expiry}。孩子第一次进入会挑一个昵称，之后所有批改记录都跟着这个码走。")


tab_gen, tab_manage, tab_calib = st.tabs(["➕ 批量生成", "📋 码列表管理", "🎯 校准记录"])

# ════════════════════════════════════════════════════════════
# Tab 1:批量生成
# ════════════════════════════════════════════════════════════
with tab_gen:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        n = st.number_input("生成数量", 1, 100, 5)
    with col2:
        quota = st.number_input("每码批改额度(篇)", 1, 100, 8)
    with col3:
        days = st.number_input("有效期(天)", 1, 365, 60)
    with col4:
        exam_level = st.selectbox("考试段", ["HCL", "O_CL", "N_CL"])
    note = st.text_input("备注(如:8月内测第一批)", "")

    if st.button("🚀 生成访问码", type="primary"):
        codes, expiry = generate_codes(int(n), int(quota), int(days), exam_level, note)
        st.session_state["last_generated"] = (codes, expiry, int(quota), exam_level)

    if st.session_state.get("last_generated"):
        _lg = st.session_state["last_generated"]
        codes, expiry, quota_shown = _lg[0], _lg[1], _lg[2]
        lvl_shown = _lg[3] if len(_lg) > 3 else ""
        st.warning("⚠️ 明文访问码只在这里显示这一次,系统只保存加密哈希。"
                   "请立刻下载 CSV 或复制保存,发放给家长。刷新页面后无法再查看!")
        for code in codes:
            st.code(code)
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["访问码", "额度(篇)", "有效期至", "考试段", "备注"])
        for code in codes:
            w.writerow([code, quota_shown, expiry, lvl_shown, note])
        st.download_button("⬇️ 下载 CSV 清单", buf.getvalue().encode("utf-8-sig"),
                           file_name="access_codes.csv", mime="text/csv")

        with st.expander("📋 发码消息(逐条复制,直接粘贴到 WhatsApp)"):
            for code in codes:
                st.code(build_parent_message(code, quota_shown, expiry, app_link), language=None)

        if st.button("✅ 我已保存,清除显示", key="btn_clear_generated"):
            st.session_state.pop("last_generated", None)
            st.rerun()

# ════════════════════════════════════════════════════════════
# Tab 2:码列表管理
# ════════════════════════════════════════════════════════════
with tab_manage:
    rows = list_codes()
    if not rows:
        st.info("还没有生成过访问码。")
    else:
        tu_map = today_usage_map()
        only_active = st.checkbox("只看启用中的码", value=False, key="filter_active")
        shown_rows = [r for r in rows if r["is_active"]] if only_active else rows

        st.caption(f"每码每日限 {DAILY_LIMIT} 篇 · 共 {len(rows)} 个码"
                   f"(启用中 {sum(1 for r in rows if r['is_active'])} 个)")
        table = [{
            "码ID": r["id"],
            "昵称": r["nickname"] or "(未领取)",
            "已用/额度": f"{r['essays_used']}/{r['essays_total']}",
            "今日已用": f"{tu_map.get(r['id'], 0)}/{DAILY_LIMIT}",
            "有效期至": r["expiry"],
            "状态": "✅ 启用" if r["is_active"] else "🚫 已停用",
            "最近使用": (r["last_used"] or "")[:16].replace("T", " "),
            "备注": r["note"] or "",
        } for r in shown_rows]
        st.dataframe(table, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 单码操作(泄露处置 / 查使用记录)")

        def _fmt_code_row(r):
            state = "启用" if r["is_active"] else "已停用"
            nick = r["nickname"] or "(未领取)"
            note_short = (r["note"] or "")[:10]
            return (f"#{r['id']} · {nick} · 已用{r['essays_used']}/{r['essays_total']}"
                    f" · {state}" + (f" · {note_short}" if note_short else ""))

        sel_row = st.selectbox("选择访问码", shown_rows, format_func=_fmt_code_row,
                               key="sel_code_row")
        sel = sel_row["id"]

        c1, c2, c3 = st.columns(3)
        with c1:
            if sel_row["is_active"]:
                if st.button("🚫 停用此码", key="btn_deact"):
                    deactivate_code(sel)
                    st.success(f"码 #{sel} 已停用。")
                    st.rerun()
            else:
                if st.button("✅ 重新启用", key="btn_react"):
                    reactivate_code(sel)
                    st.success(f"码 #{sel} 已重新启用。")
                    st.rerun()
        with c2:
            if st.button("♻️ 作废并重发新码", key="btn_reissue",
                         disabled=not sel_row["is_active"]):
                result = reissue_code(sel)
                if result:
                    new_code, remaining, expiry = result
                    st.session_state["last_reissued"] = (sel, new_code, remaining, expiry)
                st.rerun()
        with c3:
            st.caption("停用 = 立即拦截,可随时重新启用。\n重发 = 旧码作废,剩余额度转入新码。")

        with st.expander(f"📜 码 #{sel} 的使用记录(最近 20 次)"):
            logs = get_usage_log(sel)
            if logs:
                for lg in logs:
                    st.text(f"{lg['used_at'][:19].replace('T',' ')}  提交#{lg['submission_id']}")
            else:
                st.info("还没有使用记录。")

        if st.session_state.get("last_reissued"):
            old_id, new_code, remaining, expiry = st.session_state["last_reissued"]
            st.warning(f"⚠️ 码 #{old_id} 已作废。新码明文只显示这一次,请立即复制发给家长:")
            st.code(new_code)
            st.caption(f"剩余额度 {remaining} 篇已转入,有效期至 {expiry}。昵称沿用原码。")
            st.code(build_parent_message(new_code, remaining, expiry, app_link), language=None)
            if st.button("我已保存,清除显示", key="btn_clear_reissue"):
                st.session_state.pop("last_reissued", None)
                st.rerun()

# ════════════════════════════════════════════════════════════
# Tab 3:校准记录(学生填了学校老师分数的提交 = 免费校准样本)
# 2026-07-05 升级:内容/语文分拆列 + 分文体命中率 + CSV 导出
# 这就是 P0 评分校准批量测试的记录表,不需要另建 Excel
# ════════════════════════════════════════════════════════════
with tab_calib:
    samples = list_calibration_samples()
    if not samples:
        st.info("还没有校准样本。学生提交作文时填写'学校老师给的分数'后,这里会自动汇总 AI 分 vs 老师分。")
    else:
        diffs = [s["diff"] for s in samples if s["diff"] is not None]
        if diffs:
            within3 = sum(1 for d in diffs if abs(d) <= 3)
            high = sum(1 for d in diffs if d > 3)
            low = sum(1 for d in diffs if d < -3)
            st.markdown(
                f"**共 {len(samples)} 份样本 · 误差 ±3 以内:{within3}/{len(diffs)} "
                f"({within3 / len(diffs) * 100:.0f}%) · 平均偏差:{sum(diffs) / len(diffs):+.1f} 分 · "
                f"偏高(>+3):{high} 份 · 偏低(<-3):{low} 份**")
            st.caption("P0 放行标准:±3 命中率 ≥ 70%。偏高/偏低若集中在同一方向,是系统性尺度问题;方向混杂则逐篇看问题类型。")

            # 分文体命中率
            by_genre = {}
            for s in samples:
                if s["diff"] is None:
                    continue
                g = s["genre"] or "(未知)"
                by_genre.setdefault(g, []).append(s["diff"])
            if len(by_genre) > 1:
                parts = []
                for g, ds in by_genre.items():
                    w3 = sum(1 for d in ds if abs(d) <= 3)
                    parts.append(f"{g} {w3}/{len(ds)}(平均 {sum(ds)/len(ds):+.1f})")
                st.markdown("分文体:" + " ｜ ".join(parts))

        _tbl = [{
            "提交#": s["submission_id"],
            "昵称": s["student_name"],
            "文体": s["genre"],
            "题目": (s["prompt_text"] or "(无题目)")[:20],
            "学校分": s["school_score"],
            "AI总分": s["ai_score"],
            "AI内容": s.get("ai_content"),
            "AI语文": s.get("ai_language"),
            "AI等级": s.get("ai_grade", ""),
            "差值(AI-老师)": s["diff"],
            "时间": (s["created_at"] or "")[:10],
        } for s in samples]
        st.dataframe(_tbl, use_container_width=True, hide_index=True)

        _cbuf = io.StringIO()
        _cw = csv.writer(_cbuf)
        _cw.writerow(["提交#", "昵称", "文体", "题目", "学校分", "AI总分",
                      "AI内容", "AI语文", "AI等级", "差值(AI-老师)", "时间", "问题类型/备注"])
        for s in samples:
            _cw.writerow([s["submission_id"], s["student_name"], s["genre"],
                          (s["prompt_text"] or "")[:30], s["school_score"],
                          s["ai_score"], s.get("ai_content"), s.get("ai_language"),
                          s.get("ai_grade", ""), s["diff"], (s["created_at"] or "")[:10], ""])
        st.download_button("⬇️ 导出校准记录 CSV(最后一列'问题类型/备注'留给你手工标注)",
                           _cbuf.getvalue().encode("utf-8-sig"),
                           file_name="校准记录.csv", mime="text/csv")

