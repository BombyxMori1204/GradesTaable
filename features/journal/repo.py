"""SQL раздела journal. Соединение передаёт сервис."""


def get_subject(con, subject_id):
    """Проверяет существование предмета."""
    return con.execute(
        "SELECT id FROM subjects WHERE id = ?", (subject_id,)
    ).fetchone()


def get_student(con, student_id):
    """Проверяет существование студента."""
    return con.execute(
        "SELECT id FROM students WHERE id = ?", (student_id,)
    ).fetchone()


def get_group(con, group_id):
    """Проверяет существование группы."""
    return con.execute(
        "SELECT id FROM groups WHERE id = ?", (group_id,)
    ).fetchone()


def get_student_group_id(con, student_id):
    """Возвращает ID группы студента."""
    row = con.execute(
        "SELECT group_id FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    return row["group_id"] if row is not None else None


def list_grades(con, subject_id=None, group_id=None, student_id=None):
    """Возвращает оценки по фильтрам; выбранные сущности без оценок тоже видны."""
    filters = []
    params = []
    if subject_id is not None:
        filters.append("su.id = ?")
        params.append(subject_id)
    if group_id is not None:
        filters.append("g.id = ?")
        params.append(group_id)
    if student_id is not None:
        filters.append("st.id = ?")
        params.append(student_id)
    where = "WHERE " + " AND ".join(filters) if filters else "WHERE gr.id IS NOT NULL"

    cursor = con.execute(
        f"""
        SELECT gr.id, st.id AS student_id, st.name AS student_name,
               g.name AS group_name, su.id AS subject_id,
               su.name AS subject_name, gr.mark
        FROM students AS st
        JOIN groups AS g ON g.id = st.group_id
        CROSS JOIN subjects AS su
        LEFT JOIN grades AS gr
          ON gr.student_id = st.id AND gr.subject_id = su.id
        {where}
        ORDER BY su.name, st.name, st.id
        """,
        params,
    )
    return [dict(row) for row in cursor.fetchall()]


def save_grade(con, student_id, subject_id, mark):
    """Создаёт оценку или обновляет её для пары студент-предмет."""
    con.execute(
        """
        INSERT INTO grades (student_id, subject_id, mark)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id, subject_id) DO UPDATE SET mark = excluded.mark
        """,
        (student_id, subject_id, mark),
    )
    row = con.execute(
        """
        SELECT gr.id, st.id AS student_id, st.name AS student_name,
               g.name AS group_name, su.id AS subject_id,
               su.name AS subject_name, gr.mark
        FROM grades AS gr
        JOIN students AS st ON st.id = gr.student_id
        JOIN groups AS g ON g.id = st.group_id
        JOIN subjects AS su ON su.id = gr.subject_id
        WHERE gr.student_id = ? AND gr.subject_id = ?
        """,
        (student_id, subject_id),
    ).fetchone()
    return dict(row)


def delete_grade(con, student_id, subject_id):
    """Удаляет оценку для пары студент-предмет."""
    cursor = con.execute(
        "DELETE FROM grades WHERE student_id = ? AND subject_id = ?",
        (student_id, subject_id),
    )
    return cursor.rowcount > 0
