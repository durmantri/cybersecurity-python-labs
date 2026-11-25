import argparse
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import requests

from labs.lab04 import analysis, api_client
from shared.student import VARIANT_NUMBER


def validate_cve_id(value: str) -> str:
    """Перевіряє формат ідентифікатора CVE."""

    if re.fullmatch(r"CVE-[0-9]{4}-[0-9]{4,}", value) is None:
        raise argparse.ArgumentTypeError(
            "Неправильний формат CVE. Приклад: CVE-2021-44228"
        )

    return value


def load_response(path: Path) -> Any:
    """Зчитує JSON-відповідь NVD із локального файла."""

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main(argv: Sequence[str] | None = None) -> int:
    """Обробляє аргументи, отримує дані та формує JSON-звіт."""

    # перевірка номер варіанта
    if (
        isinstance(VARIANT_NUMBER, bool)
        or not isinstance(VARIANT_NUMBER, int)
        or not 1 <= VARIANT_NUMBER <= 15
    ):
        print(
            "Помилка: номер варіанта повинен бути цілим числом від 1 до 15.",
            file=sys.stderr,
        )
        return 2

    # консольний інтерфейс
    parser = argparse.ArgumentParser(
        description="Перегляд інформації про CVE через NVD API"
    )

    parser.add_argument(
        "--cve", required=True, type=validate_cve_id, help="Ідентифікатор CVE"
    )

    parser.add_argument("--input", type=Path, help="Шлях до локального JSON-файла")

    args = parser.parse_args(argv)

    try:
        # якщо переданий шлях до файлу
        if args.input is not None:
            payload = load_response(args.input)

        # інакше запит APi
        else:
            payload = api_client.fetch_response(args.cve)

        # Видобування і перевірка даних з отриманого файлу
        record = analysis.extract_record(payload, args.cve)

        report = analysis.build_report(record, args.cve, VARIANT_NUMBER)

    except FileNotFoundError:
        print("Помилка: файл не знайдено.", file=sys.stderr)
        return 1

    except UnicodeDecodeError:
        print("Помилка: файл повинен бути у форматі UTF-8.", file=sys.stderr)
        return 1

    except json.JSONDecodeError:
        print("Помилка: файл містить некоректний JSON.", file=sys.stderr)
        return 1

    except OSError:
        print("Помилка: не вдалося прочитати файл.", file=sys.stderr)
        return 1

    except api_client.JSONResponseError:
        print("Помилка: NVD повернув некоректний JSON.", file=sys.stderr)
        return 1

    except api_client.HTTPStatusError as exc:
        print(f"Неочікуваний HTTP-статус: {exc.status_code}.", file=sys.stderr)
        return 1

    except requests.exceptions.Timeout:
        print("Помилка: перевищено час очікування відповіді.", file=sys.stderr)
        return 1

    except requests.exceptions.ConnectionError:
        print("Помилка: не вдалося встановити з'єднання з NVD.", file=sys.stderr)
        return 1

    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "невідомий"

        print(f"HTTP-помилка NVD. Статус: {status}.", file=sys.stderr)
        return 1

    except requests.exceptions.RequestException:
        print("Помилка під час HTTP-запиту.", file=sys.stderr)
        return 1

    except ValueError as exc:
        print(f"Помилка перевірки даних: {exc}", file=sys.stderr)
        return 1

    # Виводимо лише JSON-звіт
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
