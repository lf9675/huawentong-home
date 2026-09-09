const DEFAULT_CONFIG = {
  lessonId: "U6L3R",
  dataModule: "./reading-data.js",
  storageKey: "u6l3-reading",
};
const READING_CONFIG = { ...DEFAULT_CONFIG, ...(window.READING_CONFIG || {}) };
const { READING_LESSON, READING_TASKS } = await import(READING_CONFIG.dataModule);

const $ = (selector) => document.querySelector(selector);
const gate = $("#gate");
const classroom = $("#classroom");
const taskArea = $("#taskArea");
let classState = null;
let selectedNumber = 0;
let student = null;
let activeStage = -1;
let currentAnswer = null;
let attempt = 1;
let feedback = null;
let taskLocked = false;
let poller = null;
let stageStartedAt = Date.now();

const savedFont = Number(localStorage.getItem(`${READING_CONFIG.storageKey}-font`)) || 20;
setFont(savedFont);
document.querySelectorAll(".font-button").forEach((button) => {
  button.addEventListener("click", () => setFont(Number(button.dataset.size)));
});

function setFont(size) {
  const safe = [20, 23, 26].includes(size) ? size : 20;
  document.documentElement.style.setProperty("--reading-size", `${safe}px`);
  localStorage.setItem(`${READING_CONFIG.storageKey}-font`, String(safe));
  document.querySelectorAll(".font-button").forEach((button) => {
    button.classList.toggle("on", Number(button.dataset.size) === safe);
  });
}

async function api(body) {
  const endpoint = `/api/reading?lessonId=${encodeURIComponent(READING_CONFIG.lessonId)}`;
  const response = await fetch(endpoint, body ? {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ ...body, lessonId: READING_CONFIG.lessonId }),
  } : { cache: "no-store" });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || "暂时无法连接课堂");
    error.code = data.code;
    throw error;
  }
  return data;
}

async function loadGate() {
  try {
    classState = await api();
    renderGate();
  } catch {
    $("#gateStatus").textContent = "暂时连不上课堂，请稍后再试。";
  }
}

function renderGate() {
  const status = $("#gateStatus");
  const grid = $("#numberGrid");
  grid.innerHTML = "";
  $("#joinButton").disabled = true;

  if (!classState?.sessionId || classState.phase === "idle") {
    status.textContent = "老师还没有建立试教课堂。";
    return;
  }
  if (classState.phase === "ended") {
    status.textContent = "本次试教已经结束。";
    return;
  }

  status.textContent = classState.paused
    ? "课堂已经建立。进入后请先看老师讲解。"
    : "课堂已经开始，请点自己的编号。";
  const remembered = readIdentity();
  for (const number of classState.roster) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "number-button";
    button.textContent = number;
    if (remembered?.sessionId === classState.sessionId && remembered.no === number) {
      selectedNumber = number;
      button.classList.add("on");
      $("#joinButton").disabled = false;
    }
    button.addEventListener("click", () => {
      selectedNumber = number;
      grid.querySelectorAll("button").forEach((item) => item.classList.remove("on"));
      button.classList.add("on");
      $("#joinButton").disabled = false;
      $("#gateError").textContent = "";
    });
    grid.appendChild(button);
  }
}

$("#joinButton").addEventListener("click", async () => {
  if (!selectedNumber) return;
  $("#joinButton").disabled = true;
  $("#gateError").textContent = "";
  try {
    student = await api({ action: "join", no: selectedNumber });
    localStorage.setItem(`${READING_CONFIG.storageKey}-identity`, JSON.stringify(student));
    $("#studentIdentity").textContent = `编号 ${student.no} · 第 ${student.group} 组`;
    gate.classList.add("hidden");
    classroom.classList.remove("hidden");
    renderLessonText();
    await pullState();
    poller = window.setInterval(pullState, 2500);
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) pullState();
    });
  } catch (error) {
    $("#gateError").textContent = error.message;
    $("#joinButton").disabled = false;
  }
});

function readIdentity() {
  try {
    return JSON.parse(localStorage.getItem(`${READING_CONFIG.storageKey}-identity`) || "null");
  } catch {
    return null;
  }
}

function renderLessonText() {
  const highlights = readHighlights();
  $("#lessonText").innerHTML = "";
  for (const paragraph of READING_LESSON.paragraphs) {
    const block = document.createElement("p");
    block.className = "paragraph";
    block.dataset.id = paragraph.id;
    block.dataset.label = paragraph.label;
    for (const sentence of paragraph.sentences) {
      const span = document.createElement("span");
      span.className = `sentence${highlights.includes(sentence.id) ? " key" : ""}`;
      span.dataset.id = sentence.id;
      span.textContent = sentence.text;
      span.addEventListener("click", () => toggleHighlight(sentence.id, span));
      block.append(span, " ");
    }
    $("#lessonText").appendChild(block);
  }
}

function readHighlights() {
  if (!student?.sessionId) return [];
  try {
    return JSON.parse(localStorage.getItem(`${READING_CONFIG.storageKey}-highlights-${student.sessionId}-${student.no}`) || "[]");
  } catch {
    return [];
  }
}

function toggleHighlight(id, element) {
  const items = new Set(readHighlights());
  if (items.has(id)) items.delete(id);
  else items.add(id);
  element.classList.toggle("key", items.has(id));
  localStorage.setItem(
    `${READING_CONFIG.storageKey}-highlights-${student.sessionId}-${student.no}`,
    JSON.stringify([...items]),
  );
}

async function pullState() {
  try {
    const next = await api();
    if (!student || next.sessionId !== student.sessionId) {
      window.clearInterval(poller);
      taskArea.innerHTML = waitingHtml("课堂已经重新建立", "请刷新页面，再用自己的编号进入。");
      return;
    }
    classState = next;
    if (next.phase === "ended") {
      $("#pausedCover").classList.add("hidden");
      taskArea.innerHTML = waitingHtml("本次精读完成", "谢谢你的认真作答。结果会暂时保留30分钟，供老师查看。");
      return;
    }
    $("#pausedCover").classList.toggle("hidden", !next.paused);
    if (next.currentStage !== activeStage) {
      activeStage = next.currentStage;
      resetTaskRuntime();
      renderTask();
      focusParagraphs();
    }
  } catch {
    $("#taskFooter").textContent = "网络短暂中断，正在自动重连；已完成的作答不会消失。";
  }
}

function resetTaskRuntime() {
  stageStartedAt = Date.now();
  currentAnswer = null;
  attempt = 1;
  feedback = null;
  taskLocked = false;
  const saved = readTaskRecord(READING_TASKS[activeStage]?.id);
  if (saved) {
    taskLocked = !!saved.locked;
    attempt = saved.attempt || 1;
    feedback = saved.feedback || null;
  }
}

function readTaskRecord(taskId) {
  if (!taskId || !student) return null;
  try {
    return JSON.parse(localStorage.getItem(`${READING_CONFIG.storageKey}-task-${student.sessionId}-${student.no}-${taskId}`) || "null");
  } catch {
    return null;
  }
}

function saveTaskRecord(taskId) {
  localStorage.setItem(
    `${READING_CONFIG.storageKey}-task-${student.sessionId}-${student.no}-${taskId}`,
    JSON.stringify({ attempt, locked: taskLocked, feedback }),
  );
}

function focusParagraphs() {
  const task = READING_TASKS[activeStage];
  const targets = new Set(task?.paragraphs || []);
  document.querySelectorAll(".paragraph").forEach((paragraph) => {
    const focused = targets.has(paragraph.dataset.id);
    paragraph.classList.toggle("focus", focused);
    paragraph.classList.toggle("dim", targets.size > 0 && !focused);
  });
  const first = document.querySelector(".paragraph.focus");
  if (first) $("#readingPane").scrollTo({ top: Math.max(0, first.offsetTop - 90), behavior: "smooth" });
}

function renderTask() {
  const task = READING_TASKS[activeStage];
  if (!task) {
    taskArea.innerHTML = waitingHtml("等待老师", "老师开放任务后，这里会自动更新。");
    return;
  }
  $("#skillChip").textContent = task.skill;
  $("#progressText").textContent = `${activeStage + 1} / ${READING_TASKS.length}`;
  $("#progressBar").style.width = `${((activeStage + 1) / READING_TASKS.length) * 100}%`;
  $("#taskFooter").textContent = `建议用时 ${task.minutes} 分钟 · 第一次答错先看定位提示，再订正一次`;

  taskArea.innerHTML = "";
  const title = document.createElement("h2");
  title.textContent = task.title;
  const instruction = document.createElement("p");
  instruction.className = "instruction";
  instruction.textContent = task.instruction;
  taskArea.append(title, instruction);

  if (feedback) taskArea.appendChild(feedbackElement(feedback));
  if (taskLocked) return;

  if (task.type === "choice" || task.type === "multi") renderOptions(task);
  if (task.type === "classify") renderClassify(task);
  if (task.type === "match") renderMatch(task);
  if (task.type === "paragraph-choice") renderParagraphChoice(task);
  if (task.type === "order") renderOrder(task);

  const submit = document.createElement("button");
  submit.type = "button";
  submit.id = "submitTask";
  submit.className = "primary-button wide";
  submit.textContent = attempt === 1 ? "提交答案" : "提交订正";
  submit.disabled = !answerComplete(task);
  submit.addEventListener("click", () => submitTask(task, submit));
  taskArea.appendChild(submit);
}

function renderOptions(task) {
  if (task.type === "choice") currentAnswer = null;
  else currentAnswer = [];
  task.options.forEach((text, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "option-button";
    button.innerHTML = `<span class="letter">${"ABCD"[index]}</span><span>${escapeHtml(text)}</span>`;
    button.addEventListener("click", () => {
      if (task.type === "choice") {
        currentAnswer = index;
        taskArea.querySelectorAll(".option-button").forEach((item) => item.classList.remove("on"));
        button.classList.add("on");
      } else {
        const set = new Set(currentAnswer);
        if (set.has(index)) set.delete(index);
        else set.add(index);
        currentAnswer = [...set];
        button.classList.toggle("on", set.has(index));
      }
      updateSubmit(task);
    });
    taskArea.appendChild(button);
  });
}

function renderClassify(task) {
  currentAnswer = Array(task.items.length).fill(null);
  task.items.forEach((text, itemIndex) => {
    const card = document.createElement("div");
    card.className = "work-card";
    const copy = document.createElement("p");
    copy.textContent = text;
    const row = document.createElement("div");
    row.className = "category-row";
    task.categories.forEach((category, categoryIndex) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "category-button";
      button.textContent = category;
      button.addEventListener("click", () => {
        currentAnswer[itemIndex] = categoryIndex;
        row.querySelectorAll("button").forEach((item) => item.classList.remove("on"));
        button.classList.add("on");
        updateSubmit(task);
      });
      row.appendChild(button);
    });
    card.append(copy, row);
    taskArea.appendChild(card);
  });
}

function renderMatch(task) {
  currentAnswer = Array(task.left.length).fill(null);
  task.left.forEach((text, itemIndex) => {
    const card = document.createElement("div");
    card.className = "work-card";
    const copy = document.createElement("p");
    copy.textContent = text;
    const row = document.createElement("div");
    row.className = "category-row";
    task.right.forEach((option, optionIndex) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "category-button";
      button.textContent = option;
      button.addEventListener("click", () => {
        currentAnswer[itemIndex] = optionIndex;
        row.querySelectorAll("button").forEach((item) => item.classList.remove("on"));
        button.classList.add("on");
        updateSubmit(task);
      });
      row.appendChild(button);
    });
    card.append(copy, row);
    taskArea.appendChild(card);
  });
}

function renderParagraphChoice(task) {
  currentAnswer = Array(task.rows.length).fill(null);
  task.rows.forEach((rowData, rowIndex) => {
    const card = document.createElement("div");
    card.className = "work-card paragraph-choice-card";
    const label = document.createElement("p");
    label.className = "paragraph-choice-label";
    label.textContent = rowData.label;
    const prompt = document.createElement("span");
    prompt.className = "paragraph-choice-prompt";
    prompt.textContent = rowData.prompt || "选择最能承担这一作用的句子：";
    const row = document.createElement("div");
    row.className = "paragraph-choice-row";
    rowData.options.forEach((option, optionIndex) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "category-button paragraph-choice-button";
      button.textContent = option;
      button.addEventListener("click", () => {
        currentAnswer[rowIndex] = optionIndex;
        row.querySelectorAll("button").forEach((item) => item.classList.remove("on"));
        button.classList.add("on");
        updateSubmit(task);
      });
      row.appendChild(button);
    });
    card.append(label, prompt, row);
    taskArea.appendChild(card);
  });
}

function renderOrder(task) {
  currentAnswer = [];
  const pool = document.createElement("div");
  pool.className = "order-pool";
  const box = document.createElement("div");
  box.className = "order-box";

  task.items.forEach((text, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "order-button";
    button.textContent = text;
    button.addEventListener("click", () => {
      currentAnswer.push(index);
      button.disabled = true;
      drawOrder(task, box);
      updateSubmit(task);
    });
    pool.appendChild(button);
  });

  const reset = document.createElement("button");
  reset.type = "button";
  reset.className = "mini-button";
  reset.textContent = "重新排列";
  reset.addEventListener("click", () => {
    currentAnswer = [];
    pool.querySelectorAll(".order-button").forEach((button) => { button.disabled = false; });
    drawOrder(task, box);
    updateSubmit(task);
  });
  taskArea.append(pool, box, reset);
}

function drawOrder(task, box) {
  box.innerHTML = currentAnswer.length
    ? currentAnswer.map((index, position) => (
      `<span class="order-item">${position + 1}. ${escapeHtml(task.items[index])}</span>`
    )).join("")
    : '<span class="note">依次点选上面的卡片</span>';
}

function updateSubmit(task) {
  const button = $("#submitTask");
  if (button) button.disabled = !answerComplete(task);
}

function answerComplete(task) {
  if (task.type === "choice") return Number.isInteger(currentAnswer);
  if (task.type === "multi") return Array.isArray(currentAnswer) && currentAnswer.length === task.answer.length;
  if (["classify", "match", "paragraph-choice", "order"].includes(task.type)) {
    const length = task.type === "match"
      ? task.left.length
      : task.type === "paragraph-choice"
        ? task.rows.length
        : task.items.length;
    return Array.isArray(currentAnswer) && currentAnswer.length === length
      && currentAnswer.every((value) => Number.isInteger(value));
  }
  return false;
}

async function submitTask(task, button) {
  button.disabled = true;
  try {
    const result = await api({
      action: "submit",
      no: student.no,
      taskId: task.id,
      attempt,
      answer: currentAnswer,
      elapsed: Math.round((Date.now() - stageStartedAt) / 1000),
    });

    if (result.held) {
      taskLocked = true;
      feedback = { kind: "plain", title: "答案已经记录", text: "先不揭晓。完成全文学习后，再回看你最初的判断。" };
    } else if (result.correct) {
      taskLocked = true;
      feedback = { kind: "good", title: attempt === 1 ? "第一次就答对了" : "订正成功", text: result.explain || task.explain };
    } else if (result.canRetry) {
      attempt = 2;
      feedback = {
        kind: "bad",
        title: "先别看答案，回到课文定位",
        text: [result.diagnosis, result.hint || task.hint].filter(Boolean).join(" "),
      };
      currentAnswer = null;
    } else {
      taskLocked = true;
      feedback = { kind: "bad", title: "这一步还没有掌握", text: result.explain || task.explain };
    }
    saveTaskRecord(task.id);
    renderTask();
  } catch (error) {
    feedback = { kind: "bad", title: "暂时没有提交成功", text: error.message };
    renderTask();
    if (error.code === "STAGE_CHANGED") pullState();
  }
}

function feedbackElement(item) {
  const box = document.createElement("div");
  box.className = `feedback ${item.kind === "plain" ? "" : item.kind}`;
  box.innerHTML = `<b>${escapeHtml(item.title)}</b>${escapeHtml(item.text)}`;
  return box;
}

function waitingHtml(title, text) {
  return `<div class="waiting-card"><div class="icon">📖</div><h2>${escapeHtml(title)}</h2><p>${escapeHtml(text)}</p></div>`;
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

loadGate();
