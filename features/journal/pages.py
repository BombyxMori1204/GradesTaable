"""HTML-страница журнала."""

from flask import render_template
from . import bp


@bp.get("/journal")
def index():
    """Возвращает страницу журнала."""
    return render_template("journal/index.html", active_page="journal")
