"""Бизнес-правила и транзакции раздела students."""

import sqlite3
from db import connect_db
from . import repo


def list_students():
    """Возвращает записи справочника.

    Returns:
        list[dict]: Данные для JSON-ответа.
    """
    con = connect_db()
    try:
        return repo.list_students(con)
    finally:
        con.close()


def save_student(name, group_id, record_id=None):
    """Проверяет данные студента и сохраняет запись одной транзакцией.

    Args:
        name (str): ФИО из JSON-запроса.
        group_id (int): ID выбранной группы.
        record_id (int | None): ID записи при редактировании.

    Returns:
        dict: Сохранённая запись с неизменным ID.

    Raises:
        ValueError: ФИО некорректно или группа не выбрана.
        LookupError: Редактируемая запись отсутствует.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Введите ФИО.")
    name = name.strip()
    if len(name) > 50:
        raise ValueError("ФИО должно быть не длиннее 50 символов.")
    if isinstance(group_id, bool) or not isinstance(group_id, int) or group_id <= 0:
        raise ValueError("Выберите группу.")
    con = connect_db()
    try:
        with con:
            if not repo.group_exists(con, group_id):
                raise ValueError("Выбранная группа не найдена.")
            if record_id is not None and repo.get_student(con, record_id) is None:
                raise LookupError("Студент не найден.")
            if record_id is None:
                record_id = repo.insert_student(con, name, group_id)
            else:
                repo.update_student(con, name, group_id, record_id)
            result = repo.get_student(con, record_id)
        return result
    finally:
        con.close()


def delete_student(record_id):
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
            if repo.get_student(con, record_id) is None:
                raise LookupError("Студент не найден.")
            repo.delete_student(con, record_id)
    except sqlite3.IntegrityError as error:
        raise ValueError("У студента есть оценки. Сначала удалите оценки.") from error
    finally:
        con.close()
