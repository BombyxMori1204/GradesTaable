"""Blueprint функционального раздела subjects."""

from flask import Blueprint

bp = Blueprint(
    "subjects", __name__, template_folder="templates",
    static_folder="static", static_url_path="/subjects/static",
)

# Импорт после создания bp позволяет зарегистрировать декораторы.
from . import pages, api
