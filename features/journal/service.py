"""Бизнес-правила и транзакции раздела journal."""

from db import connect_db
from . import repo


def _positive_id(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"Некорректный идентификатор: {label}.")
    return value


def _optional_query_id(value, label):
    if value is None:
        return None
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Некорректный идентификатор: {label}.") from error
    if str(result) != value or result <= 0:
        raise ValueError(f"Некорректный идентификатор: {label}.")
    return result


def list_grades(subject_id=None, group_id=None, student_id=None):
    """Возвращает оценки, проверяя выбранные фильтры."""
    subject_id = _optional_query_id(subject_id, "предмет")
    group_id = _optional_query_id(group_id, "группа")
    student_id = _optional_query_id(student_id, "студент")
    con = connect_db()
    try:
        if subject_id is not None and repo.get_subject(con, subject_id) is None:
            raise LookupError("Предмет не найден.")
        if group_id is not None and repo.get_group(con, group_id) is None:
            raise LookupError("Группа не найдена.")
        if student_id is not None and repo.get_student(con, student_id) is None:
            raise LookupError("Студент не найден.")
        if group_id is not None and student_id is not None:
            student_group_id = repo.get_student_group_id(con, student_id)
            if student_group_id != group_id:
                raise ValueError("Выбранный студент не входит в эту группу.")
        return repo.list_grades(con, subject_id, group_id, student_id)
    finally:
        con.close()


def save_grade(student_id, subject_id, mark):
    """Проверяет и сохраняет оценку в транзакции."""
    student_id = _positive_id(student_id, "студент")
    subject_id = _positive_id(subject_id, "предмет")
    if isinstance(mark, bool) or not isinstance(mark, int) or mark not in (2, 3, 4, 5):
        raise ValueError("Оценка должна быть целым числом от 2 до 5.")

    con = connect_db()
    try:
        with con:
            if repo.get_student(con, student_id) is None:
                raise LookupError("Студент не найден.")
            if repo.get_subject(con, subject_id) is None:
                raise LookupError("Предмет не найден.")
            return repo.save_grade(con, student_id, subject_id, mark)
    finally:
        con.close()
