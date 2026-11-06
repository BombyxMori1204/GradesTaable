"""HTTP и JSON раздела journal."""

from flask import request
from . import bp, service


@bp.get("/api/journal")
def get_grades():
    """Возвращает оценки с необязательными фильтрами."""
    items = service.list_grades(
        request.args.get("subject_id"),
        request.args.get("group_id"),
        request.args.get("student_id"),
    )
    return {"items": items}


@bp.post("/api/journal/grades")
def save_grade():
    """Создаёт оценку или изменяет существующую."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Ожидается JSON-объект.")
    item = service.save_grade(
        data.get("student_id"),
        data.get("subject_id"),
        data.get("mark"),
    )
    return {"item": item}
