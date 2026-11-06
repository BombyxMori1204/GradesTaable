import {requestJSON} from "/static/js/api.js";
import {cell, emptyRow, message, busy, fillOptions} from "/static/js/ui.js";

const head = document.querySelector("#report-head");
const body = document.querySelector("#report-body");
const groupFilter = document.querySelector("#filter-group");
const noGradesHead = document.querySelector("#no-grades-head");
const noGradesBody = document.querySelector("#no-grades-body");
const groupAverageHead = document.querySelector("#group-average-head");
const groupAverageBody = document.querySelector("#group-average-body");
const lowAverageHead = document.querySelector("#low-average-head");
const lowAverageBody = document.querySelector("#low-average-body");
let subjects = [];
let groups = [];
let students = [];
let grades = [];

function headerCell(value, className = "") {
  const th = document.createElement("th");
  th.textContent = value;
  th.className = className;
  th.scope = "col";
  return th;
}

function renderSimpleTable(tableHead, tableBody, headers, rows, emptyText) {
  const headerRow = document.createElement("tr");
  for (const header of headers) {
    headerRow.append(headerCell(header));
  }
  tableHead.replaceChildren(headerRow);
  tableBody.replaceChildren();

  if (!rows.length) {
    emptyRow(tableBody, headers.length, emptyText);
    return;
  }

  for (const values of rows) {
    const row = document.createElement("tr");
    for (const value of values) {
      row.append(cell(value));
    }
    tableBody.append(row);
  }
}

function render() {
  const groupId = groupFilter.value;
  const visibleStudents = groupId
    ? students.filter(function(student) { return student.group_id === Number(groupId); })
    : students;
  const visibleStudentIds = new Set(visibleStudents.map(function(student) { return student.id; }));
  const visibleGroups = groupId
    ? groups.filter(function(group) { return group.id === Number(groupId); })
    : groups;
  const groupNames = new Map(groups.map(function(group) { return [group.id, group.name]; }));
  const marksByStudent = new Map();
  const gradesByStudent = new Map();

  for (const grade of grades) {
    if (grade.mark === null || !visibleStudentIds.has(grade.student_id)) continue;
    if (!marksByStudent.has(grade.student_id)) marksByStudent.set(grade.student_id, []);
    marksByStudent.get(grade.student_id).push(grade.mark);
    if (!gradesByStudent.has(grade.student_id)) gradesByStudent.set(grade.student_id, new Map());
    gradesByStudent.get(grade.student_id).set(grade.subject_id, grade.mark);
  }

  const headerRow = document.createElement("tr");
  headerRow.append(headerCell("Студент", "report-student"));
  for (const subject of subjects) {
    headerRow.append(headerCell(subject.name, "report-grade"));
  }
  headerRow.append(headerCell("Средний балл", "report-average"));
  head.replaceChildren(headerRow);
  body.replaceChildren();

  if (visibleStudents.length) {
    for (const student of visibleStudents) {
      const row = document.createElement("tr");
      row.append(cell(student.name));
      const studentGrades = gradesByStudent.get(student.id) || new Map();
      const marks = marksByStudent.get(student.id) || [];

      for (const subject of subjects) {
        const mark = studentGrades.get(subject.id);
        const gradeCell = cell(mark, "report-grade");
        if (mark !== undefined) {
          gradeCell.classList.add("mark-" + mark);
          gradeCell.setAttribute("aria-label", student.name + ", " + subject.name + ": оценка " + mark);
        }
        row.append(gradeCell);
      }

      row.append(cell(formatAverage(marks), "report-average"));
      body.append(row);
    }
  } else {
    emptyRow(body, subjects.length + 2, groupId ? "В этой группе нет студентов" : "Студенты не найдены");
  }

  const ungradedStudents = visibleStudents
    .filter(function(student) { return !marksByStudent.has(student.id); })
    .map(function(student) { return [student.name, groupNames.get(student.group_id) || "—"]; });
  renderSimpleTable(
    noGradesHead, noGradesBody, ["Студент", "Группа"], ungradedStudents,
    groupId ? "В этой группе все студенты имеют оценки" : "Студенты без оценок не найдены"
  );

  const gradesByGroup = new Map();
  for (const student of visibleStudents) {
    const studentMarks = marksByStudent.get(student.id) || [];
    if (!gradesByGroup.has(student.group_id)) gradesByGroup.set(student.group_id, []);
    gradesByGroup.get(student.group_id).push(...studentMarks);
  }
  const groupAverages = visibleGroups.map(function(group) {
    return [group.name, formatAverage(gradesByGroup.get(group.id) || [])];
  });
  renderSimpleTable(
    groupAverageHead, groupAverageBody, ["Группа", "Средний балл"], groupAverages,
    "Группы не найдены"
  );

  const lowAverageStudents = visibleStudents
    .map(function(student) {
      const marks = marksByStudent.get(student.id) || [];
      return {student: student, marks: marks, average: marks.length ? average(marks) : null};
    })
    .filter(function(result) { return result.average !== null && result.average < 3; })
    .map(function(result) {
      return [result.student.name, groupNames.get(result.student.group_id) || "—", result.average.toFixed(2)];
    });
  renderSimpleTable(
    lowAverageHead, lowAverageBody, ["Студент", "Группа", "Средний балл"], lowAverageStudents,
    "Студентов со средним баллом ниже 3.3 нет"
  );
}

function average(marks) {
  return marks.reduce(function(total, mark) { return total + mark; }, 0) / marks.length;
}

function formatAverage(marks) {
  return marks.length ? average(marks).toFixed(2) : "—";
}

async function initialize() {
  busy(true);
  message("Загрузка...");
  try {
    const [subjectsResponse, groupsResponse, studentsResponse, gradesResponse] = await Promise.all([
      requestJSON("/api/subjects"),
      requestJSON("/api/groups"),
      requestJSON("/api/students"),
      requestJSON("/api/journal")
    ]);
    subjects = subjectsResponse.items;
    groups = groupsResponse.items;
    students = studentsResponse.items;
    grades = gradesResponse.items;
    fillOptions(groupFilter, groupsResponse.items, function(group) { return group.name; });
    render();
    message();
  } catch (error) {
    message(error.message, true);
    emptyRow(body, subjects.length + 2, "Данные не загружены");
    emptyRow(noGradesBody, 2, "Данные не загружены");
    emptyRow(groupAverageBody, 2, "Данные не загружены");
    emptyRow(lowAverageBody, 3, "Данные не загружены");
  } finally {
    busy(false);
  }
}

groupFilter.addEventListener("change", render);

initialize();
