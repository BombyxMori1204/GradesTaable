"""HTML-страница отчетов."""

from flask import render_template
from . import bp


@bp.get("/reports")
def index():
    """Возвращает страницу сводных оценок."""
    return render_template("reports/index.html", active_page="reports")
