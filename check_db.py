"""Контроль БД из терминала без графического окна."""

import sys
from db import connect_db


def check_database(require_baseline=False):
    """Проверяет внешние ключи и печатает количество записей.

    Args:
        require_baseline (bool): Требовать исходное состояние.

    Returns:
        dict: Количество записей в таблицах.

    Raises:
        AssertionError: Нарушены связи или начальные количества.
    """
    con = connect_db()
    try:
        enabled = con.execute("PRAGMA foreign_keys").fetchone()[0]
        violations = con.execute("PRAGMA foreign_key_check").fetchall()
        counts = {}
        print("foreign_keys: " + str(enabled))
        print("foreign_key_check: " + str(len(violations)))
        for table in ("groups", "students", "subjects", "grades"):
            counts[table] = con.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
            print(table + ": " + str(counts[table]))
        no_grades = con.execute("SELECT COUNT(*) FROM students AS s LEFT JOIN grades AS gr ON gr.student_id = s.id WHERE gr.id IS NULL").fetchone()[0]
        print("students_without_grades: " + str(no_grades))
        assert enabled == 1, "Проверка внешних ключей выключена"
        assert not violations, "Нарушены внешние ключи"
        if require_baseline:
            assert counts == {"groups": 3, "students": 60, "subjects": 3, "grades": 162}, "Сначала восстановите исходные данные"
            assert no_grades == 6, "Ожидалось шесть студентов без оценок"
        print("PASS: база прошла проверку")
        return counts
    finally:
        con.close()


if __name__ == "__main__":
    check_database("--baseline" in sys.argv)
