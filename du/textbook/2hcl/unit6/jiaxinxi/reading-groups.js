export function parseRosterText(text) {
  const rows = String(text || "").split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const students = [];
  const seen = new Set();
  for (const [index, row] of rows.entries()) {
    const parts = row.split(/[\s,，、:：]+/).filter(Boolean);
    const number = Number(parts[0]);
    const level = parts[1];
    if (!Number.isInteger(number) || number < 1 || number > 99 || !["好", "中", "差"].includes(level)) {
      throw new Error(`第 ${index + 1} 行格式不正确，请使用“编号 程度”，例如“4 好”。`);
    }
    if (seen.has(number)) throw new Error(`编号 ${number} 重复了。`);
    seen.add(number);
    students.push({ no: number, level });
  }
  if (!students.length) throw new Error("请先粘贴学生编号与语文程度。");
  return students.sort((a, b) => a.no - b.no);
}

export function makeBalancedGroups(students, count) {
  if (!Number.isInteger(count) || count < 2 || count > 12) throw new Error("小组数量必须是2至12。");
  if (students.length < count * 3) throw new Error("人数太少，无法保证每组都有好、中、差三种程度。");

  const groups = Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    students: [],
    counts: { 好: 0, 中: 0, 差: 0 },
  }));
  const targetSizes = Array.from(
    { length: count },
    (_, index) => Math.floor(students.length / count) + (index < students.length % count ? 1 : 0),
  );
  const byLevel = Object.fromEntries(["好", "中", "差"].map((level) => [
    level,
    students.filter((student) => student.level === level),
  ]));

  for (const level of ["好", "中", "差"]) {
    if (byLevel[level].length < count) {
      throw new Error(`“${level}”程度只有 ${byLevel[level].length} 人，无法做到每组至少一人。`);
    }
  }

  const baseOrders = {
    好: [...groups.keys()],
    差: [...groups.keys()].reverse(),
    中: [...groups.keys()].map((_, index) => (index + Math.floor(count / 2)) % count),
  };
  const extras = [];
  for (const level of ["好", "差", "中"]) {
    const list = byLevel[level];
    list.slice(0, count).forEach((student, index) => {
      addStudent(groups[baseOrders[level][index]], student);
    });
    extras.push(...list.slice(count));
  }

  for (const student of extras) {
    const candidates = groups
      .filter((group, index) => group.students.length < targetSizes[index])
      .sort((a, b) => (
        a.counts[student.level] - b.counts[student.level]
        || (a.students.length / targetSizes[a.id - 1]) - (b.students.length / targetSizes[b.id - 1])
        || a.id - b.id
      ));
    if (!candidates.length) throw new Error("自动分组失败，请调整小组数量。");
    addStudent(candidates[0], student);
  }
  return groups;
}

function addStudent(group, student) {
  group.students.push(student);
  group.counts[student.level] += 1;
}
