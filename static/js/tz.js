// Определяем offset пользователя и отправляем на сервер.
// getTimezoneOffset() возвращает минуты со знаком "наоборот" (для UTC+3 → -180),
// поэтому инвертируем.
(function () {
  var offset = -new Date().getTimezoneOffset(); // минуты, напр. 180
  var cookieValue = "tz_offset=" + offset + "; path=/; max-age=" +
    (365 * 24 * 3600) + "; SameSite=Lax";

  document.cookie = cookieValue;

  // Если сервер не увидел cookie при первой загрузке — перезагружаем ОДИН раз
  try {
    var hadCookie = (document.cookie.indexOf("tz_offset=") !== -1);
    if (!hadCookie && !sessionStorage.getItem("tz_synced")) {
      sessionStorage.setItem("tz_synced", "1");
      location.reload();
      return;
    }
  } catch (e) { /* sessionStorage может быть отключён */ }

  // Дублируем через API (для случая с отключёнными cookie)
  fetch("/api/tz", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ offset: offset }),
    credentials: "same-origin",
  }).catch(function () {});
})();