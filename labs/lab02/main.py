import argparse
import json
import logging
import os
import pathlib
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from labs.lab02.task1 import Admin, User, UserAccount
from labs.lab02.task2 import audit_dictionary

logger = logging.getLogger(__name__)


def setup_logging(log_file_path: pathlib.Path):
    """Налаштування логування в консоль та у файл."""
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file_path, encoding="utf-8"),
        ],
    )


def run_demo():
    print("=== ДЕМОНСТРАЦІЯ РОБОТИ СИСТЕМИ===\n")

    print("1. Створення користувача та перевірка валідації email")
    user = User(username="user1", email="good123@gmail.com", role="User")
    user.set_password("Secret123!")
    print(f"Створено користувача: {user}")
    try:
        user.email = "bad_email"
        print(f"Email змінено на поганий{user.email}")
    except ValueError as e:
        print(f"помилка email: {e}")
    user.email = "petro789@ukr.net"
    print(f"email успішно оновлено: {user.email}")

    print("\n2. Перевірка класу Admin та прав:")
    admin = Admin(
        username="admin",
        email="admin123@company.com",
        permissions=["read", "write"],
    )
    admin.set_password("AdminPass2026!")
    print(admin)
    admin.grant_permission("delete")
    print(f"Після додавання права 'delete': {admin.permissions}")
    admin.revoke_permission("read")
    print(f"Після видалення права 'read': {admin.permissions}")

    print("\n3. Демонстрація UserAccount:")
    account = UserAccount(user)

    success = account.login("user1", "WrongPass", "192.168.1.10")
    print(f"Успішний вхід з неправильним паролем: {success}")

    success = account.login("user1", "Secret123!", "192.168.1.10")
    print(f"Успішний вхід з правильним паролем: {success}")
    print(f"Статус автентифікації: {account.is_authenticated()}")

    print("\n4. Використання __getitem__ та __setitem__:")
    print(
        f"Отримання логіна та емейлу через ключ: {account['username'], account['email']}"
    )
    try:
        account["email"] = "Validated_s@gmail.com"
        print(f"Результат заміни емейлу через ключ: {account['email']}")
    except ValueError as e:
        print(e)

    print("\n5. Вихід із системи:")
    account.logout()
    print(f"Активний: {account.is_authenticated()}")

    print("\n6. Записи журналу AuditLog:")
    account.audit.show_all()


def run_analyze(args):
    setup_logging(pathlib.Path(args.log_file))

    wordlist_path = pathlib.Path(args.wordlist)
    stats = audit_dictionary(wordlist_path, args.min_length, args.top_masks)

    print("\n=== Password Dictionary Audit Summary ===")
    print(f"Total Passwords : {stats['total_passwords']:,}")
    print(
        f"Weak Passwords (<{args.min_length}) :"
        f" {stats['weak_passwords']:,} ({stats['weak_percentage']}%)"
    )
    print(f"Average Length : {stats['average_length']} characters")

    print(f"\n=== Top-{args.top_masks} Password Masks ===")
    for idx, item in enumerate(stats["top_masks"], start=1):
        print(
            f"{idx}. Mask ({item['mask']}) : {item['count']:,}"
            f" ({item['percentage']}%) [e.g. {item['example']}]"
        )

    output_path = pathlib.Path(args.output_stats)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

    logger.info(f"Dictionary statistics saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Cybersecurity Python Labs - Lab 02")
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Доступні команди"
    )

    # demo для tsk 1
    subparsers.add_parser("demo", help="Запустити демонстрацію Завдання 1")

    # analyze для task 2
    analyze_parser = subparsers.add_parser(
        "analyze", help="Запустити аудит словника паролів (Завдання 2)"
    )
    analyze_parser.add_argument(
        "--wordlist",
        type=str,
        required=True,
        help="Шлях до файлу зі словником паролів",
    )
    analyze_parser.add_argument(
        "--min-length",
        type=int,
        default=8,
        help="Мінімальна довжина слабких паролів",
    )
    analyze_parser.add_argument(
        "--top-masks", type=int, default=5, help="Кількість топових масок"
    )
    analyze_parser.add_argument(
        "--output-stats",
        type=str,
        default="labs/lab02/data/mask_audit_report.json",
        help="Шлях для збереження JSON звіту",
    )
    analyze_parser.add_argument(
        "--log-file",
        type=str,
        default="labs/lab02/data/audit.log",
        help="Шлях до файлу логів",
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        run_analyze(args)


if __name__ == "__main__":
    main()
