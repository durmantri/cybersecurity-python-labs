import json
import logging
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SEED_JSON_PATH = Path("labs/lab03/data/seed.json")


def seed_database() -> None:
    """Читає дані з seed.json та початково заповнює базу даних в одній транзакції"""
    if not SEED_JSON_PATH.exists():
        logger.error(f"Файл початкових даних не знайдено за шляхом: {SEED_JSON_PATH}")
        return

    # ініціалізація бд
    initialize_database()

    # Читання json.seed
    try:
        data = json.loads(SEED_JSON_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"Помилка читання JSON-файлу: {e}")
        return

    # атрибути дб
    categories = data.get("categories", [])
    records = data.get("records", [])

    with closing(get_connection()) as connection:
        cursor = connection.cursor()

        # Перевірка чи база вже заповнена
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM records")
        records_count = cursor.fetchone()[0]

        if categories_count > 0 or records_count > 0:
            logger.info("База даних вже містить дані.Повторне заповнення пропущено..")
            return

        try:
            with connection:
                # Вставка категорій із фіксованими id з JSON
                for cat in categories:
                    connection.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (cat["id"], cat["name"]),
                    )

                # Вставка записів
                for rec in records:
                    connection.execute(
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

            logger.info("Базу даних успішно заповнено початковими даними з seed.json")

        except sqlite3.IntegrityError as e:
            # rollback
            logger.error(f"Порушення цілісності даних (транзакцію скасовано): {e}")
            raise
        except sqlite3.Error as e:
            logger.error(
                f"Помилка бази даних під час заповнення (транзакцію скасовано): {e}"
            )
            raise


if __name__ == "__main__":
    seed_database()
