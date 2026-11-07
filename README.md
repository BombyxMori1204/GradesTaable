# Электронный журнал

Электронный журнал для работы с оценками студентов, предметами. Минимально рабочая версия.

# Стек: 

Python 3, Flask 3, SQLite, HTML, CSS и JavaScript без фронтенд-фреймворков. Серверная часть разделена на функциональные модули Flask Blueprint с отдельными слоями API, бизнес-логики и доступа к данным. Клиентская часть обращается к JSON API через Fetch.

## Запуск в Debian Linux

Один раз подготовьте системные пакеты:

~~~bash
sudo apt update
sudo apt install python3 python3-venv python3-pip sqlite3 unzip
~~~

После распаковки архива:

~~~bash
cd journal-starter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python prepare_db.py
python check_db.py --baseline
python app.py
~~~

Откройте http://127.0.0.1:5000/. Остановка сервера: Ctrl+C.
Повторный запуск после закрытия терминала:

~~~bash
cd journal-starter
source .venv/bin/activate
python app.py
~~~

## Исходная база и восстановление

База instance/journal.db создаётся явно. Исходные данные: 3 группы БЭИ2301,
БЭИ2302, БЭИ2303, по 20 студентов, 3 предмета и 162 оценки. Без оценок остаются
студенты с ID 10, 20, 30, 40, 50, 60. Группы и предметы можно добавлять.
Оценка одна на пару студент и предмет. Пустая ячейка означает отсутствие строки,
а не оценку 0. Email необязателен, одинаковые имена и email допустимы.

Для восстановления остановите сервер и выполните:

~~~bash
python prepare_db.py
python check_db.py --baseline
python app.py
~~~

Восстановление заменяет текущие учебные данные исходными. Схема и заполнение
выполняются одной транзакцией. При SQL-ошибке скрипт откатывает изменения.
Обработчик with con фиксирует или откатывает транзакцию, а соединение
дополнительно закрывается в finally. Репозитории commit не вызывают.

Чтобы обновить существующую базу для каскадного удаления оценок при удалении
предмета, остановите сервер и один раз выполните `python migrate_subject_grade_cascade.py`.
Миграция сохраняет существующие данные; повторный запуск безопасен.

## Консоль SQLite

Во втором терминале из корня проекта:

~~~bash
sqlite3 instance/journal.db
~~~

Внутри консоли:

~~~sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
.headers on
.mode column
SELECT g.name, COUNT(s.id) AS students
FROM groups AS g LEFT JOIN students AS s ON s.group_id = g.id
GROUP BY g.id, g.name;
PRAGMA foreign_key_check;
.quit
~~~

foreign_keys должен вернуть 1; foreign_key_check не должен вернуть строк.
Настройка включается для каждого соединения отдельно до BEGIN.

## Вертикальные срезы

Каждый каталог features/groups, subjects, students, journal, reports
объединяет один функциональный раздел. Blueprint создаётся в __init__.py
и регистрируется в app.py. pages.py возвращает только HTML. api.py читает
HTTP и JSON. service.py проверяет бизнес-правила, открывает соединение и
управляет транзакцией. repo.py выполняет SQL через переданное соединение.
HTML и JS находятся внутри соответствующего среза.

Общие части: db.py, templates/base.html, templates/partials/header.html,
templates/partials/footer.html, static/css/styles.css, static/js/api.js,
static/js/ui.js. Переходы между разделами обычными ссылками. Действия
пользователя обрабатывает JS, который вызывает JSON API.
