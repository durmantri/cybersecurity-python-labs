import os
import sys

from labs.lab02.task1 import Admin, User, UserAccount

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


def run_demo():
    print("=== ДЕМОНСТРАЦІЯ РОБОТИ СИСТЕМИ ===\n")

    # створення користувача та валідація email
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

    # створення адміністратора та робота з правами
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

    # демонстрація UserAccount
    print("\n3. Демонстрація UserAccount:")
    account = UserAccount(user)

    # невдалий вхід
    success = account.login("user1", "WrongPass", "192.168.1.10")
    print(f"Успішний вхід з неправильним паролем: {success}")

    # успішний вхід
    success = account.login("user1", "Secret123!", "192.168.1.10")
    print(f"Успішний вхід з правильним паролем: {success}")
    print(f"Статус автентифікації: {account.is_authenticated()}")

    # спеціальні методи __getitem__ та __setitem__
    print("\n4. Використання __getitem__ та __setitem__:")
    print(
        f"Отримання логіна та емейлу через ключ: {account['username'], account['email']}"
    )
    try:
        account["email"] = "Validated_s@gmail.com"
        print(f"Результат заміни емейлу через ключ: {account['email']}")
    except ValueError as e:
        print(e)

    # вихід із системи
    print("\n5. Вихід із системи:")
    account.logout()
    print(f"Активний: {account.is_authenticated()}")

    # журнал аудиту
    print("\n6. Записи журналу AuditLog:")
    account.audit.show_all()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    else:
        print("вірна команда: python -m labs.lab02.main demo")
