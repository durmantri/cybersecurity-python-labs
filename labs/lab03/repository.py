import sqlite3
from contextlib import closing
from typing import Any

from labs.lab03.database import get_connection

# Категорії


def create_category(name: str) -> int:
    """Створити нову категорію. Повертає id створеної категорії."""
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO categories (name) VALUES (?)",
            (name,),
        )
        connection.commit()
        return cursor.lastrowid


def get_categories() -> list[dict[str, Any]]:
    """Отримати список усіх категорій."""
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def delete_empty_category(category_id: int) -> bool:
    """
    Видалити порожню категорію.
    Повертає True, якщо видалено, або викликає помилку / повертає False,
    якщо категорія не існує чи містить записи.
    """
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        connection.commit()
        return cursor.rowcount > 0


# Записи


def create_record(
    code: str, title: str, category_id: int, value: float, status: str
) -> dict[str, Any]:
    """Додати новий запис і повернути його разом із id та назвою категорії."""
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (code, title, category_id, value, status),
            )
            record_id = cursor.lastrowid

        return get_record_by_id(record_id)


def get_record_by_id(record_id: int) -> dict[str, Any] | None:
    """Отримати один запис за його id з назвою категорії."""
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
            """,
            (record_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Отримати список записів за фільтрами."""
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = """
            SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE 1=1
        """
        params: list[Any] = []

        if category_id is not None:
            query += " AND r.category_id = ?"
            params.append(category_id)

        if status is not None:
            query += " AND r.status = ?"
            params.append(status)

        if min_value is not None:
            query += " AND r.value >= ?"
            params.append(min_value)

        if q is not None:
            query += " AND instr(r.title, ?) > 0"
            params.append(q)

        query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def update_record(
    record_id: int, code: str, title: str, category_id: int, value: float, status: str
) -> dict[str, Any] | None:
    """Оновлює поля які можна змінювати."""
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE records
                SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                WHERE id = ?
                """,
                (code, title, category_id, value, status, record_id),
            )
            if cursor.rowcount == 0:
                return None

        return get_record_by_id(record_id)


def delete_record(record_id: int) -> bool:
    """Видалити запис за id. Повертає True у разі успіху."""
    with closing(get_connection()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        return cursor.rowcount > 0


def create_records_bulk(records_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Пакетне додавання записів за одну транзакцію ."""
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        with connection:
            cursor = connection.cursor()
            inserted_ids = []

            for rec in records_data:
                cursor.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rec["code"],
                        rec["title"],
                        rec["category_id"],
                        rec["value"],
                        rec["status"],
                    ),
                )
                inserted_ids.append(cursor.lastrowid)

        result = []
        for rid in inserted_ids:
            rec_data = get_record_by_id(rid)
            if rec_data:
                result.append(rec_data)
        return result
