import json

from labs.lab04 import main


def test_main_local_json(tmp_path, monkeypatch, capsys):
    """Успішний json та відсутність мережевого запиту"""

    # тестовий json
    test_nvd_sample = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2099-10001",
                    "sourceIdentifier": "training@example.invalid",
                    "published": "2026-01-01T00:00:00.000",
                    "lastModified": "2026-10-26T00:00:00.000",
                    "vulnStatus": "Analyzed",
                    "descriptions": [
                        {
                            "lang": "en",
                            "value": "Synthetic vulnerability for offline API testing.",
                        }
                    ],
                    "metrics": {
                        "cvssMetricV31": [
                            {
                                "source": "nvd@nist.gov",
                                "type": "Primary",
                                "cvssData": {
                                    "version": "3.1",
                                    "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                                    "attackVector": "NETWORK",
                                    "attackComplexity": "LOW",
                                    "privilegesRequired": "NONE",
                                    "userInteraction": "NONE",
                                    "scope": "UNCHANGED",
                                    "confidentialityImpact": "HIGH",
                                    "integrityImpact": "HIGH",
                                    "availabilityImpact": "HIGH",
                                    "baseScore": 9.8,
                                    "baseSeverity": "CRITICAL",
                                },
                            }
                        ]
                    },
                }
            }
        ]
    }
    json_test_file = tmp_path / "test.json"
    json_test_file.write_text(json.dumps(test_nvd_sample), encoding="utf-8")

    # заборона мережевого запиту
    def fail_if_network(cve_id):
        raise AssertionError("Мережевий запит не має проходити")

    monkeypatch.setattr(main.api_client, "fetch_response", fail_if_network)

    # Запуск
    exit_code = main.main(["--cve", "CVE-2099-10001", "--input", str(json_test_file)])

    # Перевірка коду 0
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""

    # Перевірка json
    report = json.loads(captured.out)
    assert report["cve_id"] == "CVE-2099-10001"
    assert report["decision"] == "review"


def test_main_invalid_json(tmp_path, capsys):
    """Запит з пошкодженим файлом json"""

    # тестовий json
    bad_json_test_file = tmp_path / "test_broken.json"
    bad_json_test_file.write_text("{josn", encoding="utf-8")

    # Запуск
    exit_code = main.main(
        ["--cve", "CVE-2099-10001", "--input", str(bad_json_test_file)]
    )

    # Перевірка коду 1
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err != ""


def test_main_missing_file(tmp_path, capsys):
    """Запит з неіснуючим шляхом до файлу json"""

    # тестовий json
    no_json_test_file = tmp_path / "test_no_file.json"

    # Запуск
    exit_code = main.main(
        ["--cve", "CVE-2099-10001", "--input", str(no_json_test_file)]
    )

    # Перевірка коду 1
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err != ""
