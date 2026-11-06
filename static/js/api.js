/** Выполняет JSON-запрос, отдельно обрабатывая сеть, HTTP и ответ 204. */
export async function requestJSON(url, method = "GET", data = null) {
  const options = {method: method, headers: {}};
  if (data !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }
  let response;
  try { response = await fetch(url, options); }
  catch (error) { throw new Error("Нет связи с сервером. Проверьте его запуск."); }
  if (response.status === 204) return null;
  let payload;
  try { payload = await response.json(); }
  catch (error) { throw new Error("Сервер вернул ответ не в формате JSON."); }
  if (!response.ok) throw new Error(payload.error || "Ошибка HTTP " + response.status);
  return payload;
}
