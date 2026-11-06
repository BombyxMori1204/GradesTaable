"""HTTP и JSON раздела groups. SQL и бизнес-правила находятся ниже."""

from flask import request
from . import bp, service


@bp.get("/api/groups")
def get_items():
    """Возвращает список справочника.

    Returns:
        dict: Объект с массивом items.
    """
    return {"items": service.list_groups()}


@bp.post("/api/groups")
@bp.post("/api/groups/<int:record_id>")
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
    item = service.save_group(data.get("name"), record_id)
    return {"item": item}, 201 if record_id is None else 200


@bp.delete("/api/groups/<int:record_id>")
def delete_item(record_id):
    """Вызывает удаление и возвращает пустой ответ.

    Args:
        record_id (int): ID из адреса.

    Returns:
        tuple: Пустое тело и статус 204.
    """
    service.delete_group(record_id)
    return "", 204
