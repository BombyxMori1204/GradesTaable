"""Безопасно обновляет существующую БД для каскадного удаления оценок."""

import sqlite3
from pathlib import Path

import db


def migrate_database(path=None):
    """Добавляет ON DELETE CASCADE, сохраняя предметы и оценки."""
    target = Path(path) if path is not None else db.DATABASE
    if not target.exists():
        raise RuntimeError("Сначала выполните python prepare_db.py")

    con = sqlite3.connect(target)
    try:
        foreign_keys = con.execute("PRAGMA foreign_key_list(grades)").fetchall()
        subject_foreign_key = next(
            (row for row in foreign_keys if row[2] == "subjects" and row[3] == "subject_id"),
            None,
        )
        if subject_foreign_key is None:
            raise RuntimeError("В таблице grades не найдена связь с subjects.")
        if subject_foreign_key[6].upper() == "CASCADE":
            return

        con.execute("PRAGMA foreign_keys = OFF")
        con.execute("BEGIN")
        con.execute(
            """
            CREATE TABLE grades_with_cascade (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES students(id),
                subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                mark INTEGER NOT NULL CHECK(mark IN (2, 3, 4, 5)),
                UNIQUE(student_id, subject_id)
            )
            """
        )
        con.execute(
            """
            INSERT INTO grades_with_cascade (id, student_id, subject_id, mark)
            SELECT id, student_id, subject_id, mark FROM grades
            """
        )
        con.execute("DROP TABLE grades")
        con.execute("ALTER TABLE grades_with_cascade RENAME TO grades")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Обнаружены нарушенные внешние ключи после миграции.")
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    migrate_database()
    print("Каскадное удаление оценок включено.")
