import {requestJSON} from "/static/js/api.js";
import {cell, message, busy, actions, emptyRow} from "/static/js/ui.js";
const API = "/api/groups";
const body = document.querySelector("#table-body");
const editor = document.querySelector("#editor");
const form = document.querySelector("#edit-form");
const idInput = document.querySelector("#record-id");
const nameInput = document.querySelector("#record-name");
const confirmation = document.querySelector("#confirmation");
let items = [], pendingId = null, loaded = false;
nameInput.maxLength = 50;

/** Отправляет добавление или переименование записи. */
async function saveRecord(recordId, payload) {
  const url = recordId ? API + "/" + recordId : API;
  return requestJSON(url, "POST", payload);
}

/** Отправляет удаление записи. */
async function deleteRecord(recordId) {
  return requestJSON(API + "/" + recordId, "DELETE");
}

/** Строит таблицу по массиву из API. */
function render() {
  body.replaceChildren();
  if (!items.length) { emptyRow(body, 3); return; }
  for (const item of items) {
    const row = document.createElement("tr"); row.append(cell(item.name));
    row.append(cell(item.student_count, "number"));
    const td = document.createElement("td"); td.append(actions(item.id)); row.append(td); body.append(row);
  }
}

/** Обновляет данные, сохраняя старую таблицу при неудачном запросе. */
async function load(successText = "") {
  busy(true); message("Загрузка...");
  try { items = (await requestJSON(API)).items; loaded = true; render(); message(successText); }
  catch (error) {
    message((successText ? successText + " Обновление списка не удалось. " : "") + error.message, true);
    if (!loaded) emptyRow(body, 3, "Данные не загружены");
  } finally { busy(false); }
}

/** Открывает одну форму для создания и изменения. */
function openEditor(item = null) {
  form.reset(); idInput.value = item ? String(item.id) : ""; nameInput.value = item ? item.name : "";
  document.querySelector("#editor-title").textContent = item ? "Изменение записи" : "Добавление записи";
  editor.hidden = false; confirmation.hidden = true; message(); nameInput.focus();
}

document.querySelector("#add-record").addEventListener("click", function() { openEditor(); });
document.querySelector("#cancel-edit").addEventListener("click", function() { editor.hidden = true; message(); });
form.addEventListener("submit", async function(event) {
  event.preventDefault(); const name = nameInput.value.trim();
  if (!name) { message("Введите название.", true); nameInput.focus(); return; }
  busy(true);
  try {
    await saveRecord(idInput.value ? Number(idInput.value) : null, {name: name});
    editor.hidden = true; form.reset(); await load("Изменения сохранены.");
  } catch (error) { message(error.message, true); }
  finally { busy(false); }
});
body.addEventListener("click", function(event) {
  const button = event.target.closest("button[data-action]"); if (!button) return;
  const item = items.find(function(record) { return record.id === Number(button.dataset.id); }); if (!item) return;
  if (button.dataset.action === "edit") { openEditor(item); return; }
  pendingId = item.id; editor.hidden = true; confirmation.hidden = false;
  document.querySelector("#confirmation-text").textContent = "Удалить «" + item.name + "»?"; message();
});
document.querySelector("#cancel-delete").addEventListener("click", function() { pendingId = null; confirmation.hidden = true; });
document.querySelector("#confirm-delete").addEventListener("click", async function() {
  if (pendingId === null) return; busy(true);
  try { await deleteRecord(pendingId); confirmation.hidden = true; pendingId = null; await load("Запись удалена."); }
  catch (error) { message(error.message, true); } finally { busy(false); }
});
load();
