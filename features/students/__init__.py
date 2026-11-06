"""Blueprint функционального раздела students."""

from flask import Blueprint

bp = Blueprint(
    "students", __name__, template_folder="templates",
    static_folder="static", static_url_path="/students/static",
)

# Импорт после создания bp позволяет зарегистрировать декораторы.
from . import pages, api
