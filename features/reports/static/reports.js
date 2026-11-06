import {requestJSON} from "/static/js/api.js";
import {cell, emptyRow, message, busy, fillOptions} from "/static/js/ui.js";

const head = document.querySelector("#report-head");
const body = document.querySelector("#report-body");
const groupFilter = document.querySelector("#filter-group");
let subjects = [];
let students = [];
let grades = [];

function headerCell(value, className = "") {
  const th = document.createElement("th");
  th.textContent = value;
  th.className = className;
  th.scope = "col";
  return th;
}

function render() {
  const groupId = groupFilter.value;
  const visibleStudents = groupId
    ? students.filter(function(student) { return student.group_id === Number(groupId); })
    : students;
  const headerRow = document.createElement("tr");
  headerRow.append(headerCell("Студент", "report-student"));
  for (const subject of subjects) {
    headerRow.append(headerCell(subject.name, "report-grade"));
  }
  headerRow.append(headerCell("Средний балл", "report-average"));
  head.replaceChildren(headerRow);
  body.replaceChildren();

  if (!visibleStudents.length) {
    emptyRow(body, subjects.length + 2, groupId ? "В этой группе нет студентов" : "Студенты не найдены");
    return;
  }

  const gradesByStudent = new Map();
  for (const grade of grades) {
    if (!gradesByStudent.has(grade.student_id)) {
      gradesByStudent.set(grade.student_id, new Map());
    }
    gradesByStudent.get(grade.student_id).set(grade.subject_id, grade.mark);
  }

  for (const student of visibleStudents) {
    const row = document.createElement("tr");
    row.append(cell(student.name));
    const studentGrades = gradesByStudent.get(student.id) || new Map();
    const marks = [];

    for (const subject of subjects) {
      const mark = studentGrades.get(subject.id);
      const gradeCell = cell(mark, "report-grade");
      if (mark !== undefined) {
        gradeCell.classList.add("mark-" + mark);
        gradeCell.setAttribute("aria-label", student.name + ", " + subject.name + ": оценка " + mark);
        marks.push(mark);
      }
      row.append(gradeCell);
    }

    const average = marks.length
      ? (marks.reduce(function(total, mark) { return total + mark; }, 0) / marks.length).toFixed(2)
      : "—";
    row.append(cell(average, "report-average"));
    body.append(row);
  }
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
    students = studentsResponse.items;
    grades = gradesResponse.items;
    fillOptions(groupFilter, groupsResponse.items, function(group) { return group.name; });
    render();
    message();
  } catch (error) {
    message(error.message, true);
    emptyRow(body, subjects.length + 2, "Данные не загружены");
  } finally {
    busy(false);
  }
}

groupFilter.addEventListener("change", render);

initialize();
