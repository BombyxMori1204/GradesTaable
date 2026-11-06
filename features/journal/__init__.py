"""Blueprint функционального раздела journal."""

from flask import Blueprint

bp = Blueprint(
    "journal", __name__, template_folder="templates",
    static_folder="static", static_url_path="/journal/static",
)

from . import pages, api
