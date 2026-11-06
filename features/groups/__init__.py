"""Blueprint функционального раздела groups."""

from flask import Blueprint

bp = Blueprint(
    "groups", __name__, template_folder="templates",
    static_folder="static", static_url_path="/groups/static",
)

# Импорт после создания bp позволяет зарегистрировать декораторы.
from . import pages, api
