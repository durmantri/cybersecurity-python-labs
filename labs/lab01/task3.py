import csv
import hashlib
import json
import os
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path

from rich.console import Console
from rich.table import Table

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import VARIANT_NUMBER

users_to_register = (
    ("Root", "xc3we34e1q511"),
    ("pi", "raspbe321rry"),
    ("admin", "Admin213213"),
    ("root", "8888ds8812"),
    ("Adam", "xrewmhdipc32"),
    ("support", "supporttttttt"),
    ("Unix", "Onix1233fdk"),
    ("nokturnal", "mo0rtummm"),
    ("Ryzen", "Sskdw21fs0fk"),
    ("user_043912", "pilinesad3453"),
)

MIN_LENGTH = 9
CSV_PATH = Path("labs/lab01/data/users.csv")
LOG_PATH = Path("labs/lab01/data/logs.json")

salt = "0000" + str(VARIANT_NUMBER)


class ValidationError(Exception):
    pass


def generate_hash(password: str, salt: str = "00000") -> str:
    """Хешування паролю за допомогою алгоритму blake2s та солі"""

    if not password or not salt:
        raise ValueError("Пароль або сіль порожні")

    if len(password) < MIN_LENGTH:
        raise ValidationError(f"Пароль не відповідає мінімальній довжині:{MIN_LENGTH}")

    # шифрування
    salted_pass = password + salt
    cipher = hashlib.blake2s(salted_pass.encode("utf-8"))
    return cipher.hexdigest()


def create_user(username, password) -> tuple[str, str]:
    """Створює кортеж з логіну користувача та його хешу"""

    hash1 = generate_hash(password, salt)
    return (username, hash1)


def create_users(users_list: tuple):
    """Обробляє список користувачів отриманий з create_user
    та записує його в users.csv"""

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    total_users_list = []

    # обробка кортежу
    for login, passwd in users_list:
        try:
            new_user = create_user(login, passwd)
            total_users_list.append(new_user)

        except (ValueError, ValidationError) as error:
            print(error)
    try:
        # запис рядка в csv файл
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(total_users_list)

    except FileNotFoundError:
        print("файл не знайдено")
    except PermissionError:
        print("немає прав доступу до файлу ")
    except OSError:
        print("помилка вводу/виводу ")


def log_event(func):
    """Записує спробу логіну в файл logs.json"""

    @wraps(func)
    def wrapper(*args, **kwargs):

        # визначається ім'я користувача через kwargs фбо args
        username = kwargs.get("username") or args[0]
        result_status = "failure"
        try:
            res = func(*args, **kwargs)
            if res is True:
                result_status = "success"
            return res
        except Exception:
            result_status = "failure"
            raise
        finally:
            # вивід тільки введених логіна та пароля
            clean_args = []
            for arg in args[:2]:
                clean_args.append(str(arg))

            log_entry = {
                "event": func.__name__,
                "user": str(username),
                "result": result_status,
                "timestamp": f"{datetime.now():%Y-%m-%d %H:%M:%S}",
                "args": clean_args,
                "kwargs": kwargs,
            }

            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

            # читання логу
            logs = []
            if LOG_PATH.exists():
                try:
                    with open(LOG_PATH, "r", encoding="utf-8") as log:
                        logs = json.load(log)
                except json.JSONDecodeError:
                    logs = []

            # новий запис
            logs.append(log_entry)
            with open(LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=4)

    return wrapper


@log_event
def login(username: str, password: str, users_db: list) -> bool:
    """ПЕревіряє введені дані користувача з хешованими в user_db"""

    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми")

    hashed_input = generate_hash(password, salt)

    # пошук користувача та порівняння хешу
    for db_user, db_pass in users_db:
        if db_user == username:
            return db_pass == hashed_input
    return False


def main():
    console = Console()

    # створення списку користувачів
    create_users(users_to_register)

    # читання бази даних
    users_db = []
    with open(CSV_PATH, mode="r", encoding="utf-8") as read_file:
        csv_read = csv.reader(read_file)
        users_db = list(csv_read)

    # таблиця rich
    table = Table(title="База даних", title_justify="center")
    table.add_column("Логін", justify="center")
    table.add_column("Хеш", justify="center")

    for usr, hash in users_db:
        table.add_row(usr, hash)

    console.print(table)

    # авторизація
    user_input = input("Введіть логін користувача: ")
    pass_input = input("Введіть пароль: ")

    try:
        logged = login(user_input, pass_input, users_db)
        if logged:
            print("Авторизовано")
        else:
            print("Невірний логін або пароль")
    except ValueError:
        print("Невірний ввід")


if __name__ == "__main__":
    main()
