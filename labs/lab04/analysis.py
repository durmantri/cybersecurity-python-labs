import math
import os
import sys
from typing import Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


def extract_record(payload: Any, cve_id: str) -> dict[str, Any] | None:
    """Перевірки для відповіді NVD"""

    if not isinstance(payload, dict):
        raise TypeError("Відповідь NVD повинна бути словником")

    if "vulnerabilities" not in payload:
        raise ValueError("Відсутнє поле vulnerabilities")

    vuln_list = payload["vulnerabilities"]

    if not isinstance(vuln_list, list):
        raise TypeError("vulnerabilities повинно бути списком")
    if len(vuln_list) > 1:
        raise ValueError("vulnerabilities повинно містити не більше одного елемента")
    if len(vuln_list) == 0:
        return None

    # перевірка  cve
    cve_list = vuln_list[0]

    if "cve" not in cve_list:
        raise ValueError("Відсутнє поле cve")

    cve = cve_list["cve"]

    if not isinstance(cve, dict):
        raise TypeError("cve повинно бути словником")

    temp_id = cve.get("id") if cve else None
    if cve_id != temp_id:
        raise ValueError("не одинакові ID")

    # перевірка статусу
    vuln_status = None

    if "vulnStatus" in cve:
        vuln_status = cve["vulnStatus"]

        if not isinstance(vuln_status, str) or not vuln_status.strip():
            raise ValueError("vulnStatus повинен бути непорожнім рядком")

    # перевірка опису
    desc_text = None

    if "descriptions" in cve:
        descriptions = cve["descriptions"]

        if not isinstance(descriptions, list):
            raise ValueError("descriptions повинно бути списком")

        for item in descriptions:
            if not isinstance(item, dict):
                raise TypeError("Елементи descriptions повинні бути словниками")

            lang = item.get("lang")
            value = item.get("value")

            if not isinstance(lang, str) or not isinstance(value, str):
                raise TypeError("lang і value повинні бути рядками")

            if lang == "en" and value.strip() and desc_text is None:
                desc_text = value

    record = {
        "description": desc_text,
        "vuln_status": vuln_status,
        "cvss_data": None,
        "score_source": None,
    }

    # перевірка rejected статусу
    if vuln_status is None or vuln_status == "Rejected":
        return record

    # перевірка чи є поле metrics
    if "metrics" not in cve:
        return record

    metrics = cve["metrics"]

    if not isinstance(metrics, dict):
        raise TypeError("Metrics має бути словником")

    # перевірка чи є поле cvssMetricV31
    if "cvssMetricV31" not in metrics:
        return record

    cvss_list = metrics["cvssMetricV31"]

    if not isinstance(cvss_list, list):
        raise TypeError("cvssMetricV31 має бути списком")

    if len(cvss_list) == 0:
        return record

    for element in cvss_list:
        if not isinstance(element, dict):
            raise TypeError("елементи cvssMetricV31 мають бути словником")

    # Перевірка type
    selected = next(
        (element for element in cvss_list if element.get("type") == "Primary"),
        cvss_list[0],
    )

    # перевірка cvssDate
    if "cvssData" not in selected or not isinstance(selected["cvssData"], dict):
        raise ValueError("cvssData повинно бути словником")

    cvss_data = selected["cvssData"]

    # перевірка baseScore
    baseScore = cvss_data.get("baseScore")

    if "baseScore" in cvss_data:
        if isinstance(baseScore, bool) or not isinstance(baseScore, (int, float)):
            raise ValueError("baseScore повинен бути числом")

        if not math.isfinite(baseScore) or not 0 <= baseScore <= 10:
            raise ValueError("baseScore має бути скінченним числом від 0 до 10")

    # перевірка необов'язкових полів cvssData
    version = cvss_data.get("version")
    vector = cvss_data.get("vectorString")

    if "version" in cvss_data:
        if not isinstance(version, str) or not version.strip():
            raise ValueError("version повинен бути непорожнім рядком")

        if version != "3.1":
            raise ValueError("Версія CVSS повинна бути 3.1")

    if (
        "vectorString" in cvss_data
        and (not isinstance(vector, str))
        or not vector.strip()
    ):
        raise ValueError("vectorString повинен бути непорожнім рядком")

    # перевірка джерела оцінки
    source = selected.get("source")

    if "source" in selected and (not isinstance(source, str)) or not source.strip():
        raise ValueError("source повинен бути непорожнім рядком")

    # збереження  оцінки
    record["score_source"] = source

    if "baseScore" not in cvss_data:
        return record

    record["cvss_data"] = cvss_data

    return record


RULES = {6: {"threshold": 7.0, "field": "integrityImpact", "expected": "HIGH"}}


def build_report(record: dict, cve_id: str, VARIANT_NUMBER: int):

    # правило варіанта
    rule = RULES[VARIANT_NUMBER].copy()
    threshold = rule["threshold"]
    field = rule["field"]
    expected = rule["expected"]

    # початкова структура report
    report = {
        "cve_id": cve_id,
        "variant": VARIANT_NUMBER,
        "description": None,
        "vuln_status": None,
        "cvss_version": None,
        "score": None,
        "score_source": None,
        "vector": None,
        "rule": rule,
        "observed": None,
        "decision": None,
    }

    # перевірка на відсутність запису
    if record is None:
        report["decision"] = "not_found"
        return report

    if not isinstance(record, dict):
        raise TypeError("record повинен бути словником або None")

    #  опис і статус
    report["description"] = record["description"]
    report["vuln_status"] = record["vuln_status"]

    vuln_status = record["vuln_status"]

    # перевірка Rejected
    if vuln_status == "Rejected":
        report["decision"] = "rejected"
        return report

    # перевірка відсутнього статусу
    if vuln_status is None:
        report["decision"] = "insufficient_data"
        return report

    # дані csvv
    cvss_data = record["cvss_data"]

    # перевірка якщо немає оцінки
    if cvss_data is None:
        report["decision"] = "insufficient_data"
        return report

    score = cvss_data["baseScore"]

    report["cvss_version"] = cvss_data.get("version")
    report["score"] = score
    report["score_source"] = record["score_source"]
    report["vector"] = cvss_data.get("vectorString")

    # перевірка поля варіанта
    if field not in cvss_data:
        report["decision"] = "insufficient_data"
        return report

    observed = cvss_data[field]
    report["observed"] = observed

    # перевірка правила варіанта
    if score >= threshold and observed == expected:
        report["decision"] = "review"
    else:
        report["decision"] = "other"

    return report
