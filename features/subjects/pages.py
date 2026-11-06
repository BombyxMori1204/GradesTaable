"""HTML-страница раздела Группы без запросов к БД."""

from flask import render_template
from . import bp


@bp.get("/subjects")
def index():
    """Возвращает структуру страницы и подключение JavaScript.

    Returns:
        str: HTML с общими шапкой и подвалом.
    """
    return render_template("subjects/index.html", active_page="subjects")
