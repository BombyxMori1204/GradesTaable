"""Бизнес-правила и транзакции раздела groups."""

import sqlite3
from db import connect_db
from . import repo


def list_groups():
    """Возвращает записи справочника.

    Returns:
        list[dict]: Данные для JSON-ответа.
    """
    con = connect_db()
    try:
        return repo.list_groups(con)
    finally:
        con.close()


def save_group(name, record_id=None):
    """Проверяет название и сохраняет запись одной транзакцией.

    Args:
        name (str): Название из JSON-запроса.
        record_id (int | None): ID записи при редактировании.

    Returns:
        dict: Сохранённая запись с неизменным ID.

    Raises:
        ValueError: Название некорректно или занято.
        LookupError: Редактируемая запись отсутствует.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Введите название.")
    name = name.strip()
    if len(name) > 50:
            raise ValueError("Допускается не более 50 символов.")
    con = connect_db()
    try:
        with con:
            if record_id is not None and repo.get_group(con, record_id) is None:
                raise LookupError("Группа не найдена.")
            if record_id is None:
                record_id = repo.insert_group(con, name)
            else:
                repo.update_group(con, name, record_id)
            result = repo.get_group(con, record_id)
        return result
    except sqlite3.IntegrityError as error:
        raise ValueError("Такое название уже существует.") from error
    finally:
        con.close()


def delete_group(record_id):
    """Удаляет запись при отсутствии зависимых данных.

    Args:
        record_id (int): Идентификатор удаляемой записи.

    Returns:
        None: Транзакция завершена.

    Raises:
        LookupError: Запись отсутствует.
        ValueError: Внешний ключ запрещает удаление.
    """
    con = connect_db()
    try:
        with con:
            if repo.get_group(con, record_id) is None:
                raise LookupError("Группа не найдена.")
            repo.delete_group(con, record_id)
    except sqlite3.IntegrityError as error:
        raise ValueError("В группе есть студенты. Сначала переведите или удалите их.") from error
    finally:
        con.close()
