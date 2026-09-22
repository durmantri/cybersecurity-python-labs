import random
from collections import Counter

from rich.console import Console
from rich.table import Table

passwords = [
    "InfoS3c@2023",
    "simple123",
    "Def3ns3@Key",
    "public",
    "Encrypt3d#Pass",
    "basic123",
    "Secur3@Analysis",
    "temp123",
    "Pr0t3ct@Data",
    "default",
]
criteria = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}
forbidden_passwords = {"simple123", "public", "basic123", "temp123", "default", "guest"}


def passwd_check(passwd: str, pass_counts: Counter) -> tuple[str, str]:
    """Перевіряє пароль на відповідність критеріям"""

    # заборонений
    if len(passwd) < criteria["min_length"] or passwd in forbidden_passwords:
        return "Заборонений", "red"

    has_lower = any(c.islower() for c in passwd)
    has_upper = any(c.isupper() for c in passwd)
    has_digit = any(c.isdigit() for c in passwd)
    has_special = any(not char.isalnum() for char in passwd)

    passed_count = sum([has_lower, has_upper, has_digit, has_special])

    # Дуже сильний
    if (
        passed_count == 4
        and len(passwd) >= criteria["min_length"] + 4
        and pass_counts[passwd] == 1
    ):
        return "Дуже сильний", "green"

    # Сильний
    if passed_count == 4:
        return "Сильний", "green"

    # Середній
    if passed_count >= 2:
        return "Середній", "yellow"

    # Слабкий
    if passed_count >= 1:
        return "Слабкий", "yellow"


def main():

    # вибір 3 рандомних паролів
    for i in range(3):
        passwords.append(random.choice(passwords))

    pass_counts = Counter(passwords)

    # таблиця rich
    table = Table()
    table.add_column("Пароль", style="white")
    table.add_column("Надійність", justify="center")

    duplicated_passwd = set()

    # відсіювання паролів що повторюються та вивід чистої таблиці
    for passwd in passwords:
        if passwd not in duplicated_passwd:
            duplicated_passwd.add(passwd)
            category, color = passwd_check(passwd, pass_counts)
            table.add_row(passwd, f"[{color}]{category}[/{color}]")

    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
