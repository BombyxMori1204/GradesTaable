import {requestJSON} from "/static/js/api.js";
import {cell, message, busy, emptyRow, fillOptions} from "/static/js/ui.js";

const API = "/api/journal";
const body = document.querySelector("#table-body");
const subjectFilter = document.querySelector("#filter-subject");
const groupFilter = document.querySelector("#filter-group");
const studentFilter = document.querySelector("#filter-student");
let items = [];
let students = [];
let loaded = false;

function render() {
  body.replaceChildren();
  if (!items.length) {
    emptyRow(body, 4, subjectFilter.value || groupFilter.value || studentFilter.value ? "Оценок нет" : "Оценки не найдены");
    return;
  }

  for (const item of items) {
    const row = document.createElement("tr");
    row.append(cell(item.student_name), cell(item.group_name), cell(item.subject_name));

    const gradeCell = document.createElement("td");
    gradeCell.className = "grade-cell";
    const select = document.createElement("select");
    select.dataset.studentId = String(item.student_id);
    select.dataset.subjectId = String(item.subject_id);
    select.setAttribute("aria-label", "Оценка: " + item.student_name + ", " + item.subject_name);
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "—";
    select.append(placeholder);
    for (const mark of [2, 3, 4, 5]) {
      const option = document.createElement("option");
      option.value = String(mark);
      option.textContent = String(mark);
      select.append(option);
    }
    select.value = item.mark === null ? "" : String(item.mark);
    gradeCell.append(select);
    row.append(gradeCell);
    body.append(row);
  }
}

async function load() {
  busy(true);
  message("Загрузка...");
  const query = new URLSearchParams();
  if (subjectFilter.value) query.set("subject_id", subjectFilter.value);
  if (groupFilter.value) query.set("group_id", groupFilter.value);
  if (studentFilter.value) query.set("student_id", studentFilter.value);
  try {
    const suffix = query.toString();
    items = (await requestJSON(API + (suffix ? "?" + suffix : ""))).items;
    loaded = true;
    render();
    message();
  } catch (error) {
    message(error.message, true);
    if (!loaded) emptyRow(body, 4, "Данные не загружены");
  } finally {
    busy(false);
  }
}

subjectFilter.addEventListener("change", load);
groupFilter.addEventListener("change", function() {
  fillStudents();
  load();
});
studentFilter.addEventListener("change", load);

body.addEventListener("change", async function(event) {
  const select = event.target.closest("select[data-student-id][data-subject-id]");
  if (!select) return;
  const studentId = Number(select.dataset.studentId);
  const subjectId = Number(select.dataset.subjectId);
  const item = items.find(function(record) {
    return record.student_id === studentId && record.subject_id === subjectId;
  });
  if (!item) return;

  const previousMark = item.mark;
  if (!select.value) {
    select.value = previousMark === null ? "" : String(previousMark);
    return;
  }

  busy(true);
  try {
    const response = await requestJSON(API + "/grades", "POST", {
      student_id: studentId,
      subject_id: subjectId,
      mark: Number(select.value)
    });
    item.mark = response.item.mark;
    message("Оценка сохранена.");
  } catch (error) {
    select.value = previousMark === null ? "" : String(previousMark);
    message(error.message, true);
  } finally {
    busy(false);
  }
});

async function initialize() {
  busy(true);
  message("Загрузка...");
  try {
    const [subjectsResponse, groupsResponse, studentsResponse] = await Promise.all([
      requestJSON("/api/subjects"),
      requestJSON("/api/groups"),
      requestJSON("/api/students")
    ]);
    fillOptions(subjectFilter, subjectsResponse.items, function(subject) { return subject.name; });
    fillOptions(groupFilter, groupsResponse.items, function(group) { return group.name; });
    students = studentsResponse.items;
    fillStudents();
    await load();
  } catch (error) {
    message(error.message, true);
    if (!loaded) emptyRow(body, 4, "Данные не загружены");
  } finally {
    busy(false);
  }
}

function fillStudents() {
  const groupId = groupFilter.value;
  const filteredStudents = groupId
    ? students.filter(function(student) { return student.group_id === Number(groupId); })
    : students;
  studentFilter.replaceChildren();
  const allOption = document.createElement("option");
  allOption.value = "";
  allOption.textContent = "Все студенты";
  studentFilter.append(allOption);
  fillOptions(studentFilter, filteredStudents, function(student) { return student.name; });
}

initialize();
