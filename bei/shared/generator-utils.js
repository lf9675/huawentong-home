export function splitTerms(value) {
  return String(value || '').split(/[\n\t,，、]+/).map(x => x.trim()).filter(Boolean);
}

export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

export function downloadText(filename, content, type='text/html') {
  const blob = new Blob([content], {type});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

export function validateQuestions(questions) {
  const errors = [];
  if (!Array.isArray(questions) || !questions.length) errors.push('没有生成任何题目。');
  (questions || []).forEach((q, i) => {
    if (!q.question) errors.push(`第 ${i + 1} 题缺少题目。`);
    if (!Array.isArray(q.options) || q.options.length < 3) errors.push(`第 ${i + 1} 题选项不足。`);
    if (!Number.isInteger(q.answer) || q.answer < 0 || q.answer >= (q.options || []).length) errors.push(`第 ${i + 1} 题答案位置错误。`);
  });
  return errors;
}
