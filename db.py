"""Общее подключение к SQLite для всех функциональных срезов."""

from pathlib import Path
import sqlite3

DATABASE = Path(__file__).resolve().parent / "instance" / "journal.db"


def connect_db():
    """Открывает соединение и включает внешние ключи до транзакции.

    Returns:
        sqlite3.Connection: Соединение, которое вызывающий код закроет.

    Raises:
        RuntimeError: База ещё не создана скриптом prepare_db.py.
    """
    if not DATABASE.exists():
        raise RuntimeError("Сначала выполните python prepare_db.py")
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con
