"""SQL раздела subjects. Соединение передаёт сервис, commit здесь отсутствует."""

def list_subjects(con):
    """Возвращает группы, включая пустые, с числом студентов.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.

    Returns:
        list[dict]: Строки результата.
    """
    cursor = con.execute(
        '''
        SELECT g.id, g.name, COUNT(gr.student_id) AS student_count FROM subjects AS g LEFT JOIN grades AS gr ON gr.subject_id = g.id GROUP BY g.id, g.name ORDER BY g.name, g.id
        ''',
        (),
    )
    return [dict(row) for row in cursor.fetchall()]


def get_subject(con, record_id):
    """Находит группу по идентификатору.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        record_id: Значение параметра запроса.

    Returns:
        dict | None: Запись либо None.
    """
    cursor = con.execute(
        '''
        SELECT id, name FROM subjects WHERE id = ?
        ''',
        (record_id,),
    )
    row = cursor.fetchone()
    return dict(row) if row is not None else None


def insert_subject(con, name):
    """Добавляет группу без фиксации транзакции.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        name: Значение параметра запроса.

    Returns:
        int: Идентификатор новой записи.
    """
    cursor = con.execute(
        '''
        INSERT INTO subjects (name) VALUES (?)
        ''',
        (name,),
    )
    return cursor.lastrowid


def update_subject(con, name, record_id):
    """Переименовывает группу, сохраняя её идентификатор.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        name: Значение параметра запроса.
        record_id: Значение параметра запроса.

    Returns:
        None: Изменения остаются в текущей транзакции.
    """
    cursor = con.execute(
        '''
        UPDATE subjects SET name = ? WHERE id = ?
        ''',
        (name, record_id),
    )


def delete_subject(con, record_id):
    """Удаляет группу; внешний ключ защищает непустую группу.

    Args:
        con (sqlite3.Connection): Соединение текущей операции.
        record_id: Значение параметра запроса.

    Returns:
        None: Изменения остаются в текущей транзакции.
    """
    cursor = con.execute(
        '''
        DELETE FROM subjects WHERE id = ?
        ''',
        (record_id,),
    )
