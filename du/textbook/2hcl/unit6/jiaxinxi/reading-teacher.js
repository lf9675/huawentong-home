const DEFAULT_CONFIG = {
  lessonId: "U6L3R",
  dataModule: "./reading-data.js",
  storageKey: "u6l3-reading",
};
const READING_CONFIG = { ...DEFAULT_CONFIG, ...(window.READING_CONFIG || {}) };
const { READING_TASKS } = await import(READING_CONFIG.dataModule);
import { makeBalancedGroups, parseRosterText } from "./reading-groups.js";

const $ = (selector) => document.querySelector(selector);
let pin = sessionStorage.getItem(`${READING_CONFIG.storageKey}-teacher-pin`) || "";
let preview = null;
let snapshot = null;
let poller = null;
let clock = null;
$("#teacherPin").value = pin;

async function api(body) {
  const response = await fetch("/api/reading", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ ...body, pin, lessonId: READING_CONFIG.lessonId }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "暂时无法连接课堂");
  return data;
}

function rememberPin() {
  pin = $("#teacherPin").value.trim();
  sessionStorage.setItem(`${READING_CONFIG.storageKey}-teacher-pin`, pin);
  return !!pin;
}

function buildPreview() {
  const students = parseRosterText($("#rosterInput").value);
  const count = Number($("#groupCount").value);
  const groups = makeBalancedGroups(students, count);
  preview = { students, groups };
  renderGroupCards($("#groupPreview"), groups, true);
  $("#setupError").textContent = `共 ${students.length} 人，已分为 ${groups.length} 组。程度标签只留在这个浏览器里。`;
  return preview;
}

$("#rosterInput").addEventListener("input", () => { preview = null; });
$("#groupCount").addEventListener("input", () => { preview = null; });

function renderGroupCards(container, groups, showLevels = false) {
  container.innerHTML = groups.map((group) => {
    const members = group.students
      ? group.students.map((student) => showLevels ? `${student.no}（${student.level}）` : student.no).join("、")
      : group.members.join("、");
    return `<div class="group-card"><b>第 ${group.id} 组</b><span>${escapeHtml(members)}</span></div>`;
  }).join("");
}

$("#previewGroups").addEventListener("click", () => {
  $("#setupError").textContent = "";
  try {
    buildPreview();
  } catch (error) {
    $("#setupError").textContent = error.message;
  }
});

$("#createClass").addEventListener("click", async () => {
  $("#setupError").textContent = "";
  if (!rememberPin()) {
    $("#setupError").textContent = "请先输入教师口令。";
    return;
  }
  try {
    const data = preview || buildPreview();
    if (!window.confirm(`将用 ${data.students.length} 人建立新的试教课堂。现有课堂数据会被清除，确定继续吗？`)) return;
    const groups = {};
    for (const group of data.groups) {
      for (const student of group.students) groups[student.no] = group.id;
    }
    snapshot = await api({
      action: "setup",
      roster: data.students.map((student) => student.no),
      groups,
    });
    openDashboard();
  } catch (error) {
    $("#setupError").textContent = error.message;
  }
});

$("#connectClass").addEventListener("click", async () => {
  $("#setupError").textContent = "";
  if (!rememberPin()) {
    $("#setupError").textContent = "请先输入教师口令。";
    return;
  }
  try {
    snapshot = await api({ action: "teacherSnapshot" });
    if (!snapshot.state?.sessionId) throw new Error("目前没有已建立的试教课堂。");
    openDashboard();
  } catch (error) {
    $("#setupError").textContent = error.message;
  }
});

function openDashboard() {
  $("#setupPanel").classList.add("hidden");
  $("#dashboard").classList.remove("hidden");
  renderDashboard();
  window.clearInterval(poller);
  poller = window.setInterval(refreshSnapshot, 3000);
  window.clearInterval(clock);
  clock = window.setInterval(renderClock, 1000);
}

async function refreshSnapshot() {
  try {
    snapshot = await api({ action: "teacherSnapshot" });
    renderDashboard();
  } catch (error) {
    $("#classStatus").textContent = `连接中断：${error.message}`;
  }
}

async function teacherAction(action, confirmText = "") {
  if (confirmText && !window.confirm(confirmText)) return;
  setControlsDisabled(true);
  try {
    snapshot = await api({ action });
    renderDashboard();
  } catch (error) {
    window.alert(error.message);
  } finally {
    setControlsDisabled(false);
  }
}

$("#togglePause").addEventListener("click", () => {
  teacherAction(snapshot?.state?.paused ? "resume" : "pause");
});
$("#nextStage").addEventListener("click", () => {
  const next = READING_TASKS[(snapshot?.state?.currentStage || 0) + 1];
  if (!next) return;
  teacherAction("next", `全班将统一进入“${next.title}”。未完成的学生会停止当前作答，确定继续吗？`);
});
$("#undoStage").addEventListener("click", () => teacherAction("undo"));
$("#endClass").addEventListener("click", () => {
  teacherAction("end", "结束后，作答数据只再保留30分钟。确定结束本次试教吗？");
});

function setControlsDisabled(disabled) {
  ["#togglePause", "#nextStage", "#undoStage", "#endClass"].forEach((selector) => {
    $(selector).disabled = disabled;
  });
}

function renderDashboard() {
  if (!snapshot?.state) return;
  const state = snapshot.state;
  const task = READING_TASKS[state.currentStage];
  $("#currentSkill").textContent = task?.skill || "课堂状态";
  $("#currentTitle").textContent = task
    ? `第 ${state.currentStage + 1} 环节：${task.title}`
    : "等待建立课堂";

  const status = $("#classStatus");
  status.classList.toggle("paused", state.paused);
  if (state.phase === "ended") {
    status.textContent = "试教已经结束。数据将在30分钟后清除。";
  } else if (state.paused) {
    status.textContent = "全班已暂停：学生可以阅读课文，但不能提交答案。";
  } else {
    status.textContent = "学生正在作答。教师可以暂停讲解，或统一进入下一环节。";
  }

  $("#togglePause").textContent = state.paused ? "开始／继续作答" : "暂停全班";
  $("#togglePause").disabled = state.phase === "ended";
  $("#nextStage").disabled = state.phase === "ended" || state.currentStage >= READING_TASKS.length - 1;
  $("#endClass").disabled = state.phase === "ended";

  renderMetrics();
  renderStudents();
  renderDashboardGroups();
  renderClock();
}

function renderMetrics() {
  const metrics = snapshot.metrics || [];
  $("#metricBody").innerHTML = metrics.map((metric, index) => {
    const active = index === snapshot.state.currentStage ? ' style="background:#f3f8f8"' : "";
    return `<tr${active}>
      <td><b>${escapeHtml(metric.skill)}</b><br><span class="note">${escapeHtml(metric.title)}</span></td>
      <td>${metric.submitted}/${snapshot.state.roster.length}</td>
      <td>${metric.firstRate}%</td>
      <td>${metric.finalRate}%</td>
      <td class="gain">${metric.gain > 0 ? "+" : ""}${metric.gain}%</td>
    </tr>`;
  }).join("");
}

function renderStudents() {
  const students = snapshot.students || [];
  let done = 0;
  let correction = 0;
  $("#studentGrid").innerHTML = students.map((student) => {
    let className = "student-tile";
    let label = "未进入";
    if (student.joined) {
      className += " joined";
      label = "进行中";
    }
    if (student.currentDone) {
      className += " done";
      label = student.needsCorrection ? "待订正" : student.corrected ? "已订正" : "已完成";
      done += 1;
    }
    if (student.needsCorrection) correction += 1;
    return `<div class="${className}"><b>${student.no}</b><span>${label}</span></div>`;
  }).join("");
  const joined = students.filter((student) => student.joined).length;
  $("#studentSummary").textContent = `已进入 ${joined}/${students.length} 人；当前任务已提交 ${done} 人；待订正 ${correction} 人。`;
}

function renderDashboardGroups() {
  const groups = new Map();
  for (const number of snapshot.state.roster) {
    const group = Number(snapshot.state.groups[number]);
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group).push(number);
  }
  renderGroupCards(
    $("#dashboardGroups"),
    [...groups.entries()].sort((a, b) => a[0] - b[0]).map(([id, members]) => ({ id, members })),
  );
}

function renderClock() {
  if (!snapshot?.state) return;
  const state = snapshot.state;
  if (state.phase === "ended" && state.expiresAt) {
    const seconds = Math.max(0, Math.ceil((state.expiresAt - Date.now()) / 1000));
    const minutes = Math.floor(seconds / 60);
    const remainder = String(seconds % 60).padStart(2, "0");
    $("#classClock").textContent = `数据剩余 ${minutes}:${remainder}`;
    return;
  }
  if (state.startedAt) {
    const minutes = Math.floor((Date.now() - state.startedAt) / 60000);
    $("#classClock").textContent = `课堂已进行 ${minutes} 分钟`;
  }
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}
