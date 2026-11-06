"""Запуск Flask и регистрация функциональных срезов."""

import sqlite3
from flask import Flask, redirect, render_template, request, url_for
from features.groups import bp as groups_bp
from features.journal import bp as journal_bp
from features.reports import bp as reports_bp
from features.subjects import bp as subjects_bp
from features.students import bp as students_bp


app = Flask(__name__)
app.json.ensure_ascii = False
for blueprint in (groups_bp, subjects_bp, students_bp, journal_bp, reports_bp):
    app.register_blueprint(blueprint)


@app.get("/")
def index():
    """Открывает раздел групп.

    Returns:
        Response: Перенаправление на первую страницу.
    """
    return redirect(url_for("groups.index"))


@app.errorhandler(ValueError)
def invalid_data(error):
    """Преобразует ошибку проверки данных в JSON.

    Args:
        error (ValueError): Ошибка бизнес-правила или запроса.

    Returns:
        tuple: JSON и HTTP-статус 400.
    """
    return {"error": str(error)}, 400


@app.errorhandler(LookupError)
def missing_record(error):
    """Сообщает об отсутствующей записи.

    Args:
        error (LookupError): Ошибка поиска записи.

    Returns:
        tuple: JSON и HTTP-статус 404.
    """
    return {"error": str(error)}, 404


@app.errorhandler(NotImplementedError)
def unfinished_operation(error):
    """Показывает ожидаемый ответ незавершённого задания.

    Args:
        error (NotImplementedError): Заглушка стартового проекта.

    Returns:
        tuple: JSON и HTTP-статус 501.
    """
    return {"error": "Операция пока не реализована."}, 501


@app.errorhandler(sqlite3.Error)
def database_error(error):
    """Скрывает технические подробности ошибки БД от интерфейса.

    Args:
        error (sqlite3.Error): Неожиданная ошибка SQLite.

    Returns:
        tuple: JSON и HTTP-статус 500.
    """
    app.logger.exception("Ошибка SQLite")
    return {"error": "Ошибка базы данных. Подробности в терминале сервера."}, 500


@app.errorhandler(404)
def missing_route(error):
    """Возвращает понятный ответ для неизвестного адреса.

    Args:
        error: HTTP-ошибка Flask.

    Returns:
        tuple: HTML либо JSON со статусом 404.
    """
    if request.path.startswith("/api/"):
        return {"error": "Адрес API не найден."}, 404
    return render_template("error.html", active_page=""), 404


@app.errorhandler(405)
def wrong_method(error):
    """Обрабатывает неподдерживаемый HTTP-метод.

    Args:
        error: HTTP-ошибка Flask.

    Returns:
        tuple: JSON и HTTP-статус 405.
    """
    return {"error": "HTTP-метод не поддерживается."}, 405


if __name__ == "__main__":
    app.run(debug=True)
