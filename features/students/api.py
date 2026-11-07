"""HTTP и JSON раздела students. SQL и бизнес-правила находятся ниже."""

from flask import request
from . import bp, service


@bp.get("/api/students")
def get_items():
    """Возвращает список справочника.

    Returns:
        dict: Объект с массивом items.
    """
    return {"items": service.list_students()}


@bp.post("/api/students")
@bp.post("/api/students/<int:record_id>")
def save_item(record_id=None):
    """Читает JSON и вызывает сохранение записи.

    Args:
        record_id (int | None): ID из адреса при изменении.

    Returns:
        tuple: Объект item и статус 201 либо 200.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Ожидается JSON-объект.")
    item = service.save_student(
        data.get("name"), data.get("group_id"), record_id, data.get("email")
    )
    return {"item": item}, 201 if record_id is None else 200


@bp.delete("/api/students/<int:record_id>")
def delete_item(record_id):
    """Вызывает удаление и возвращает пустой ответ.

    Args:
        record_id (int): ID из адреса.

    Returns:
        tuple: Пустое тело и статус 204.
    """
    service.delete_student(record_id)
    return "", 204
