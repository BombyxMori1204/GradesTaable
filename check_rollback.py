"""Проверка настоящего сервиса удаления на временной копии БД."""

from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import db
from features.students import service


def snapshot():
    """Читает все значения четырёх таблиц для сравнения.

    Returns:
        dict: Таблицы и строки в порядке идентификаторов.
    """
    con = db.connect_db()
    try:
        result = {}
        for table in ("groups", "students", "subjects", "grades"):
            result[table] = [tuple(row) for row in con.execute("SELECT * FROM " + table + " ORDER BY id")]
        return result
    finally:
        con.close()


def check_rollback():
    """Сравнивает БД до и после учебного сбоя внутри сервиса.

    Returns:
        None: Печатает результаты отката и успешного удаления.

    Raises:
        AssertionError: Откат неполный либо сервис не удаляет студента.
    """
    original_path = db.DATABASE
    with TemporaryDirectory(prefix="journal-check-") as directory:
        target = Path(directory) / "journal.db"
        source = db.connect_db()
        copied = sqlite3.connect(target)
        copied.execute("PRAGMA foreign_keys = ON")
        try:
            source.backup(copied)
        finally:
            copied.close()
            source.close()
        db.DATABASE = target
        try:
            con = db.connect_db()
            try:
                row = con.execute("SELECT student_id FROM grades ORDER BY id LIMIT 1").fetchone()
            finally:
                con.close()
            assert row is not None, "Для проверки нужен студент с оценками"
            student_id = row[0]
            before = snapshot()
            caught = False
            try:
                service.delete_student(student_id, simulate_error=True)
            except RuntimeError as error:
                caught = True
                print("Учебный сбой: " + str(error))
            assert caught, "Сервис не вызвал учебную ошибку"
            assert snapshot() == before, "Откат неполный: данные изменились"
            print("PASS: студент и все оценки сохранены после отката")
            service.delete_student(student_id)
            after = snapshot()
            expected = dict(before)
            expected["students"] = [row for row in before["students"] if row[0] != student_id]
            expected["grades"] = [row for row in before["grades"] if row[1] != student_id]
            assert after == expected, "Удаление изменило посторонние данные"
            print("PASS: обычное удаление убрало студента и его оценки")
        finally:
            db.DATABASE = original_path
    print("PASS: рабочая база не изменена проверкой")


if __name__ == "__main__":
    check_rollback()
