import logging
import re
from collections import Counter
from pathlib import Path

# логер для модуля
logger = logging.getLogger(__name__)


def create_password_mask(password: str) -> str:
    """Створює маску пароля:

    U - Upper, l - lower, d - Digit, s - Special
    """
    mask = []
    for char in password:
        if re.match(r"[A-Z]", char):
            mask.append("U")
        elif re.match(r"[a-z]", char):
            mask.append("l")
        elif re.match(r"[0-9]", char):
            mask.append("d")
        else:
            mask.append("s")
    return "".join(mask)


def password_generator(file_path: Path):
    """Генератор для почергового читання файлу"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            pwd = line.strip()
            if pwd:
                yield pwd


def audit_dictionary(file_path: Path, min_length: int, top_masks_n: int):
    logger.info(f"Processing dictionary file {file_path} using generators...")

    total_passwords = 0
    weak_passwords = 0
    total_length = 0

    mask_counter = Counter()
    mask_examples = {}

    for i, pwd in enumerate(password_generator(file_path), start=1):
        total_passwords += 1
        total_length += len(pwd)

        # Перевірка на слабкий пароль за довжиною
        if len(pwd) < min_length:
            weak_passwords += 1

        # Аналіз маски
        mask = create_password_mask(pwd)
        mask_counter[mask] += 1

        # приклад маски для статистики
        if mask not in mask_examples:
            mask_examples[mask] = pwd

        # Логування прогресу
        if i == 44:
            logger.info(f"Analyzed {i} passwords.")

    logger.info(f"Finished processing. Total analyzed: {total_passwords:,} passwords.")

    # Розрахунок метрик
    avg_length = total_length / total_passwords if total_passwords > 0 else 0
    weak_percentage = (
        (weak_passwords / total_passwords) * 100 if total_passwords > 0 else 0
    )

    top_masks = mask_counter.most_common(top_masks_n)

    # словник для JSON
    stats_report = {
        "total_passwords": total_passwords,
        "weak_passwords": weak_passwords,
        "weak_percentage": round(weak_percentage, 1),
        "average_length": round(avg_length, 1),
        "top_masks": [
            {
                "mask": m,
                "count": c,
                "percentage": round((c / total_passwords) * 100, 1),
                "example": mask_examples[m],
            }
            for m, c in top_masks
        ],
    }

    return stats_report
