/* ============================================================
   华文通 · 作文审题区  平台挂钩 hook.js
   ① 学生完成后自动把「审题卡」上传到 Google 表格
   ② 右下角加一个「AI 审题诊断」按钮
   不改动各套作文网页原有的程序；出问题时删掉页尾那一行 <script> 即可复原。
   ============================================================ */
(function () {
  "use strict";

  var C = window.XIEZUO || {};
  var TOPICS = C.TOPICS || {};

  /* ---------- 0. 小工具 ---------- */
  function txt(el) { return String((el && (el.innerText || el.textContent)) || ""); }
  function trim(s) { return String(s || "").replace(/\s+/g, " ").trim(); }

  /* ---------- 1. 我是哪一篇、第几页 ---------- */
  function whoAmI() {
    var id = (window.XIEZUO_PAGE && window.XIEZUO_PAGE.id) || "";
    if (!id) {
      var seg = location.pathname.split("/").filter(Boolean);
      id = decodeURIComponent(seg[seg.length - 2] || "");
    }
    var page = (window.XIEZUO_PAGE && window.XIEZUO_PAGE.page) ||
               (/page2/.test(location.pathname) ? 2 : 1);
    return { id: id, page: page, meta: TOPICS[id] || null };
  }
  var ME = whoAmI();
  if (!ME.meta) return;               // 不认识的页面就完全不介入

  /* ---------- 2. 姓名与班级 ---------- */
  function byPlaceholder(re) {
    var found = "";
    document.querySelectorAll("input").forEach(function (el) {
      if (found) return;
      if (re.test(el.placeholder || "") && String(el.value || "").trim()) found = el.value.trim();
    });
    return found;
  }
  function getUser() {
    var e1 = document.getElementById("stuName"), e2 = document.getElementById("stuClass");
    var n = e1 ? String(e1.value || "").trim() : "";
    var c = e2 ? String(e2.value || "").trim() : "";
    if (!n) n = byPlaceholder(/名字|姓名/);
    if (!c) c = byPlaceholder(/班|例\s*[:：]?\s*20\d/);
    if (n) return { name: n, cls: c };
    // 第二页没有输入框：从本机存档里找第一页存的资料
    for (var i = 0; i < localStorage.length; i++) {
      try {
        var o = JSON.parse(localStorage.getItem(localStorage.key(i)));
        if (o && typeof o === "object") {
          var u = (o.user && o.user.name) ? o.user : (o.name ? o : null);
          if (u && u.name) return { name: String(u.name), cls: String(u["class"] || u.cls || "") };
        }
      } catch (e) { }
    }
    // 再退一步：从网址参数拿（第一页会把资料带过来）
    try {
      var q = new URLSearchParams(location.search);
      if (q.get("name")) return { name: q.get("name"), cls: q.get("cls") || q.get("class") || "" };
    } catch (e) { }
    return { name: "", cls: "" };
  }

  /* ---------- 3. 收集学生写下的内容 ---------- */
  function labelOf(el) {
    var r = el.closest(".row");
    if (r && r.querySelector(".k")) return trim(txt(r.querySelector(".k")));
    var p = el.previousElementSibling, hop = 0;
    while (p && hop < 3) {
      var t = trim(txt(p));
      if (t && t.length <= 40) return t;
      p = p.previousElementSibling; hop++;
    }
    var box = el.closest("section,.card,.block,.stage,.task,.challenge,div");
    if (box) {
      var h = box.querySelector("h2,h3,h4,label");
      if (h && trim(txt(h))) return trim(txt(h)).slice(0, 40);
    }
    return trim(el.placeholder).slice(0, 40) || el.id || "学生填写";
  }

  function collect() {
    var out = [], seen = {};
    function push(label, text) {
      label = trim(label).slice(0, 60); text = trim(text);
      if (!text || text.length < 2 || text === "—" || text === "（未写）") return;
      var k = label + "||" + text;
      if (seen[k]) return; seen[k] = 1;
      out.push({ label: label || "未命名", text: text });
    }
    // (a) 审题卡：.row 里 .k 是栏目名，其余是内容 —— 这是最完整的一份
    document.querySelectorAll(".row").forEach(function (r) {
      var k = r.querySelector(".k");
      if (!k) return;
      var whole = txt(r), key = txt(k);
      push(key, whole.replace(key, ""));
    });
    // (b) 打字题
    document.querySelectorAll("textarea, input[type=text]").forEach(function (el) {
      if (/code|stuName|stuClass/i.test(el.id || "")) return;
      if (/名字|姓名|班|学号|第几组|口令/.test(el.placeholder || "")) return;
      push(labelOf(el), el.value);
    });
    // (c) 有些页把审题卡写成 artXxx 元素
    document.querySelectorAll("[id^=art]").forEach(function (el) {
      if (el.children.length) return;
      push("审题卡·" + el.id.replace(/^art/, ""), txt(el));
    });
    return out;
  }

  function stats() {
    var g = document.querySelectorAll(".processBox b");
    if (g.length >= 3) return { first: trim(txt(g[0])), revised: trim(txt(g[1])), revealed: trim(txt(g[2])) };
    return { first: "", revised: "", revealed: "" };
  }

  /* ---------- 4. 上传 ---------- */
  var sent = false;
  function toast(msg, ok) {
    var d = document.getElementById("xzToast");
    if (!d) {
      d = document.createElement("div"); d.id = "xzToast";
      d.style.cssText = "position:fixed;left:50%;transform:translateX(-50%);bottom:22px;z-index:99999;" +
        "padding:11px 20px;border-radius:999px;font-size:14.5px;font-family:inherit;max-width:90vw;" +
        "text-align:center;box-shadow:0 4px 18px rgba(0,0,0,.18);transition:opacity .35s";
      document.body.appendChild(d);
    }
    d.style.background = ok ? "#1F6F4A" : "#8A4B2A";
    d.style.color = "#fff"; d.textContent = msg; d.style.opacity = "1";
    setTimeout(function () { d.style.opacity = "0"; }, 4500);
  }

  function upload() {
    if (sent) return;
    var f = collect();
    if (!f.length) return;                       // 还没内容，等下一次
    if (!C.API) { sent = true; toast("未连后台：请打印或截图交给老师", false); return; }
    var u = getUser();
    if (!u.name) { sent = true; toast("找不到姓名，请截图交给老师", false); return; }
    sent = true;
    var s = stats();
    toast("正在把审题卡交给老师……", true);
    fetch(C.API, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },   // 避开跨域预检
      body: JSON.stringify({
        a: "submit", topic: ME.id, title: ME.meta.title, page: ME.page,
        cls: u.cls, name: u.name,
        first: s.first, revised: s.revised, revealed: s.revealed, fields: f
      })
    }).then(function (r) { return r.json(); })
      .then(function (j) { toast(j && j.ok ? "✓ 已交给老师" : "上传失败，请截图交给老师", !!(j && j.ok)); })
      .catch(function () { toast("网络不通，请截图交给老师", false); });
  }

  function watch() {
    var r = document.getElementById("result");
    if (!r) return;
    var go = function () { if (r.classList.contains("show")) setTimeout(upload, 400); };
    go();
    new MutationObserver(go).observe(r, { attributes: true, attributeFilter: ["class"] });
  }

  /* ---------- 5. AI 审题诊断 ---------- */
  function addAI() {
    if (!C.AI_ON || !C.AI_PROXY) return;
    if (typeof window.callAI === "function") return;    // 该页自带 AI，不重复加

    var btn = document.createElement("button");
    btn.type = "button"; btn.textContent = "AI 审题诊断";
    btn.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:99998;border:none;cursor:pointer;" +
      "padding:12px 18px;border-radius:999px;background:#B5432E;color:#fff;font-size:15px;font-weight:600;" +
      "font-family:inherit;box-shadow:0 4px 14px rgba(0,0,0,.22)";
    document.body.appendChild(btn);

    var panel = document.createElement("div");
    panel.style.cssText = "position:fixed;right:16px;bottom:72px;z-index:99998;display:none;width:min(400px,88vw);" +
      "max-height:58vh;overflow:auto;background:#fff;border:1px solid #DED7C9;border-radius:12px;padding:16px;" +
      "font-size:15px;line-height:1.8;font-family:inherit;box-shadow:0 8px 30px rgba(0,0,0,.2)";
    document.body.appendChild(panel);

    btn.onclick = function () {
      var f = collect();
      if (!f.length) { alert("先做几题、写一点内容，再让 AI 看。"); return; }
      panel.style.display = "block";
      panel.innerHTML = "<b style='color:#B5432E'>AI 审题诊断</b><br>正在看你写的内容……";
      var sys = "你是新加坡中学高级华文老师，正在指导" + ME.meta.level + "学生做作文《" + ME.meta.title +
        "》的写前审题。作文题：" + ME.meta.full + "\n" + ME.meta.prompt +
        "\n请先明确判断『可以／还不够』，再用两三句指出好在哪或缺什么，最后给一句具体的改进建议。" +
        "语气亲切但要诚实，不要一味夸奖。简体中文，120字以内，用中学生看得懂的话。";
      var usr = f.map(function (x) { return x.label + "：" + x.text; }).join("\n");
      fetch(C.AI_PROXY, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: C.AI_MODEL || "deepseek-v4-flash",
          messages: [{ role: "system", content: sys }, { role: "user", content: "学生写的内容：\n" + usr }],
          temperature: 0.4, max_tokens: 400
        })
      }).then(function (r) { return r.json(); })
        .then(function (j) {
          var t = j && j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content;
          panel.innerHTML = "<b style='color:#B5432E'>AI 审题诊断</b><br>" +
            (t ? t.replace(/\n/g, "<br>") : "AI 没有回应，请举手问老师。") +
            "<br><br><span style='font-size:13px;color:#8A857C'>AI 的意见只供参考，以老师讲评为准。</span>";
        })
        .catch(function () {
          panel.innerHTML = "<b style='color:#B5432E'>AI 审题诊断</b><br>连不上 AI。先自己对照题目要求检查，或举手问老师。";
        });
    };
  }

  function boot() { watch(); addAI(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
