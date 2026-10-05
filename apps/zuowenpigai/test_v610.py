# -*- coding: utf-8 -*-
"""v6.10 验证脚本 — 只测代码强制封顶，不调用任何 API，不花钱。
用法: python test_v610.py"""
from prompts import finalize_grade_fields, ENGINE_VERSION

def mk(content, language, axis, c_level="无"):
    return {"scores": {"content": content, "language": language,
                       "total": content + language},
            "content_gate": {"life_logic_ok": True, "detail_balance_ok": True,
                             "keyword_focus_ok": True, "ending_lyric_ok": True,
                             "keyword_misread": False,
                             "core_detail_extent": "充分",
                             "sub_point_axis": axis, "c_level": c_level,
                             "reason": "测试"}}

def ax(*verdicts):
    return [{"para_num": i + 2, "keyword": "K%d" % i, "verdict": v, "note": ""}
            for i, v in enumerate(verdicts)]

CASES = [
    # (说明, 输入内容, 输入语文, axis, c_level, 期望内容, 期望语文)
    ("T1 三段全脱轴→内容≤12、语文≤19", 24, 24, ax("换轴", "空转", "贴标签"), "无", 12, 19),
    ("T2 三段脱两段→内容≤14、语文≤23", 22, 24, ax("换轴", "空转", "紧扣"), "无", 14, 23),
    ("T3 三段脱一段→内容≤16、语文≤23", 22, 24, ax("紧扣", "紧扣", "例不对轴"), "无", 16, 23),
    ("T4 全部紧扣→不封顶(负样本,防误伤)", 24, 24, ax("紧扣", "紧扣", "紧扣"), "无", 24, 24),
    ("T5 记叙文空数组→不触发(负样本)", 24, 24, [], "无", 24, 24),
    ("T6 已在顶下方不上调(21<16? 不,15<16 保持15)", 15, 20, ax("紧扣", "换轴"), "无", 15, 20),
    ("T7 C级较严重新顶16(旧18)", 22, 24, [], "较严重", 16, 23),
    ("T8 C级严重仍14", 22, 24, [], "严重", 14, 19),
]

print("ENGINE_VERSION =", ENGINE_VERSION)
fail = 0
for name, c, l, axis, lvl, ec, el in CASES:
    fb = finalize_grade_fields(mk(c, l, axis, lvl), "HCL")
    gc, gl = fb["scores"]["content"], fb["scores"]["language"]
    ok = (gc == ec and gl == el and fb["scores"]["total"] == gc + gl)
    fail += 0 if ok else 1
    print(("  OK  " if ok else " FAIL ") + name,
          "→ 内容%s(期望%s) 语文%s(期望%s)" % (gc, ec, gl, el))
    if not ok:
        print("        auto_caps =", fb.get("auto_caps"))

# 普华 20 分制
P = [("P1 全脱轴 普华→内容≤8", 16, 16, ax("换轴", "空转"), 8),
     ("P2 脱一段 普华→内容≤11", 16, 16, ax("紧扣", "紧扣", "空转"), 11)]
for name, c, l, axis, ec in P:
    fb = finalize_grade_fields(mk(c, l, axis), "O_CL")
    gc = fb["scores"]["content"]
    ok = gc == ec
    fail += 0 if ok else 1
    print(("  OK  " if ok else " FAIL ") + name, "→ 内容%s(期望%s)" % (gc, ec))

print("\n结果:", "全部通过 ✅" if fail == 0 else "有 %d 条失败 ❌" % fail)

