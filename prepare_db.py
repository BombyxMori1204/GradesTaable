"""Создание и восстановление исходной базы одной транзакцией."""

from pathlib import Path
import sqlite3
import db

ROOT = Path(__file__).resolve().parent


def initialize_database(path=None):
    """Восстанавливает таблицы и учебные данные атомарно.

    Args:
        path (Path | None): Файл БД; по умолчанию db.DATABASE.

    Returns:
        dict: Количество записей в четырёх таблицах.

    Raises:
        RuntimeError: Начальные данные не прошли проверку.
        sqlite3.Error: SQL-ошибка; предыдущая база сохраняется.
    """
    target = Path(path) if path is not None else db.DATABASE
    target.parent.mkdir(parents=True, exist_ok=True)
    schema = (ROOT / "data/schema.sql").read_text(encoding="utf-8")
    seed = (ROOT / "data/seed.sql").read_text(encoding="utf-8")
    con = sqlite3.connect(target)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        # executescript может завершить старую транзакцию. Поэтому
        # BEGIN находится внутри скрипта, а соединение здесь новое.
        con.executescript("BEGIN;\n" + schema + "\n" + seed)
        counts = {}
        for table in ("groups", "students", "subjects", "grades"):
            counts[table] = con.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
        if counts != {"groups": 3, "students": 60, "subjects": 3, "grades": 162}:
            raise RuntimeError("Нарушено исходное количество записей.")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Обнаружены нарушенные внешние ключи.")
        con.commit()
        return counts
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    result = initialize_database()
    print("База восстановлена: " + str(db.DATABASE))
    for table, count in result.items():
        print(table + ": " + str(count))
