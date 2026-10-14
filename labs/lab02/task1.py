import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone

ITERATIONS = 100_000
SESSION_TIMEOUT_SEC = 900


class User:
    def __init__(self, username: str, email: str, role: str, active: bool = True):
        if not username:
            raise ValueError("Ім'я користувача не може бути порожнім.")
        self.username = username
        self.email = email  # Викликає setter з валідацією
        self.role = role
        self.active = active
        self.__password_hash = None
        self.__password_salt = None

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str):
        # Патерн для перевірки емейлу
        pattern = r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError("невірний формат email!")
        self.__email = value

    def set_password(self, password: str):
        if not password:
            raise ValueError("Пароль не може бути порожнім")

        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, ITERATIONS
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_hash or not self.__password_salt:
            return False
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, ITERATIONS
        )
        return hmac.compare_digest(new_hash, self.__password_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        status = "активний" if self.active else "неактивний"
        return f"Користувач: {self.username}, Email: {self.email}, Роль: {self.role} ({status})"


class Admin(User):
    def __init__(
        self, username: str, email: str, permissions=None, active: bool = True
    ):
        super().__init__(username, email, role="Admin", active=active)
        # Захист від колекції
        if permissions is None:
            self.permissions = set()
        else:
            self.permissions = set(permissions)

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self):
        base_str = super().__str__()
        rights = ", ".join(self.permissions) if self.permissions else "немає"
        return f"{base_str}, Права: [{rights}]"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        current_time = datetime.now(timezone.utc)
        self.login_time = current_time
        self.last_activity = current_time

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("Таймаут має бути додатним числом!")
        current_time = datetime.now(timezone.utc)
        elapsed = (current_time - self.last_activity).total_seconds()
        return elapsed <= timeout_sec


@dataclass
class LogRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.records = []

    def add_log(self, username: str, action: str):
        record = LogRecord(
            timestamp=datetime.now(timezone.utc), username=username, action=action
        )
        self.records.append(record)

    def show_all(self):
        for r in self.records:
            time_str = r.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"[{time_str}] Користувач: {r.username} | Дія: {r.action}")


class UserAccount:
    def __init__(self, user: User, session=None, audit_log=None):
        self.user = user
        self.session = session
        self.audit = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        if self.user.username != username or not self.user.active:
            self.audit.add_log(username, "login_failure")
            return False

        if self.user.check_password(password):
            self.session = Session(ip)
            self.session.touch()
            self.audit.add_log(username, "login_success")
            return True
        else:
            self.audit.add_log(username, "login_failure")
            return False

    def is_authenticated(self) -> bool:
        if self.session is None:
            return False
        try:
            return self.session.is_active(SESSION_TIMEOUT_SEC)
        except ValueError:
            return False

    def logout(self):
        if self.session:
            self.audit.add_log(self.user.username, "logout")
            self.session = None

    def __getitem__(self, key: str):
        if key == "user":
            return self.user
        elif key == "session":
            return self.session
        elif key == "audit":
            return self.audit
        elif key == "username":
            return self.user.username
        elif key == "email":
            return self.user.email
        elif key == "role":
            return self.user.role
        elif key == "active":
            return self.user.active
        else:
            raise KeyError(f"Невідомий ключ: {key}")

    def __setitem__(self, key: str, value):
        if key == "email":
            if not isinstance(value, str):
                raise TypeError("Email має бути рядком")
            self.user.email = value
        elif key == "active":
            if not isinstance(value, bool):
                raise TypeError("Active має бути булевим значенням")
            self.user.active = value
        elif key in ["user", "session", "audit", "username", "role"]:
            raise TypeError(f"Ключ '{key}' доступний лише для читання")
        else:
            raise KeyError(f"Невідомий ключ: {key}")
