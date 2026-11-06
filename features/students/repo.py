"""SQL раздела students. Соединение передаёт сервис, commit здесь отсутствует."""

def list_students(con):
    """Возвращает студентов с названием группы и числом оценок.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.

    Returns:
        list[dict]: Строки результата.
    """
    cursor = con.execute(
        '''
        SELECT s.id, s.name, s.group_id, g.name AS group_name,
               COUNT(gr.id) AS grade_count
        FROM students AS s
        JOIN groups AS g ON g.id = s.group_id
        LEFT JOIN grades AS gr ON gr.student_id = s.id
        GROUP BY s.id, s.name, s.group_id, g.name
        ORDER BY s.name, s.id
        ''',
        (),
    )
    return [dict(row) for row in cursor.fetchall()]


def get_student(con, record_id):
    """Находит студента по идентификатору.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        record_id: Значение параметра запроса.

    Returns:
        dict | None: Запись либо None.
    """
    cursor = con.execute(
        '''
        SELECT id, name, group_id FROM students WHERE id = ?
        ''',
        (record_id,),
    )
    row = cursor.fetchone()
    return dict(row) if row is not None else None


def group_exists(con, group_id):
    """Проверяет, существует ли группа с указанным идентификатором."""
    cursor = con.execute(
        '''
        SELECT 1 FROM groups WHERE id = ?
        ''',
        (group_id,),
    )
    return cursor.fetchone() is not None


def insert_student(con, name, group_id):
    """Добавляет студента без фиксации транзакции.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        name: Значение параметра запроса.

    Returns:
        int: Идентификатор новой записи.
    """
    cursor = con.execute(
        '''
        INSERT INTO students (name, group_id) VALUES (?, ?)
        ''',
        (name, group_id),
    )
    return cursor.lastrowid


def update_student(con, name, group_id, record_id):
    """Изменяет ФИО и группу студента.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        name: Значение параметра запроса.
        record_id: Значение параметра запроса.

    Returns:
        None: Изменения остаются в текущей транзакции.
    """
    cursor = con.execute(
        '''
        UPDATE students SET name = ?, group_id = ? WHERE id = ?
        ''',
        (name, group_id, record_id),
    )


def delete_student(con, record_id):
    """Удаляет студента; внешний ключ защищает его оценки.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        record_id: Значение параметра запроса.

    Returns:
        None: Изменения остаются в текущей транзакции.
    """
    cursor = con.execute(
        '''
        DELETE FROM students WHERE id = ?
        ''',
        (record_id,),
    )
