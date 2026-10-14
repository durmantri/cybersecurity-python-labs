import argparse
import json
import re
from collections import Counter
from pathlib import Path


def create_password_mask(password: str) -> str:
    """Створює  маску пароля:
    U - Upper
    l - lower
    d - Digit
    s - Special
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
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            pwd = line.strip()
            if pwd:
                yield pwd


def audit_dictionary(file_path: Path, min_length: int, top_masks_n: int):
    print(f"[INFO] Processing dictionary file {file_path} using generators...")

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
            print(f"[INFO] Analyzed {i} passwords.")

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


def main2():
    # CLI аргументи
    parser = argparse.ArgumentParser(description="Password Dictionary Auditor")
    parser.add_argument(
        "--wordlist",
        type=str,
        required=True,
        help="Шлях до файлу зі словником паролів",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=8,
        help="Мінімальна довжина слабких паролів",
    )
    parser.add_argument(
        "--top-masks", type=int, default=5, help="Кількість топових масок"
    )
    parser.add_argument(
        "--output-stats",
        type=str,
        default="labs/lab02/data/mask_audit_report.json",
        help="Шлях для збереження JSON",
    )

    args = parser.parse_args()
    # шлях до файлу з паролями
    wordlist_path = Path(args.wordlist)

    stats = audit_dictionary(wordlist_path, args.min_length, args.top_masks)

    # виведення результатів
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

    # збереження статистики в JSON
    output_path = Path(args.output_stats)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

    print(f"\n[INFO] Dictionary statistics saved to {output_path}")


if __name__ == "__main__":
    main2()
