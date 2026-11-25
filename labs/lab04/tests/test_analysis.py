import pytest

from labs.lab04 import analysis
from shared.student import VARIANT_NUMBER

CVE_ID = "CVE-2099-10001"
VECTOR = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"


# функції для створення тестових даних
def make_metric(score=8.8, metric_type="Primary", source="test-source"):
    return {
        "type": metric_type,
        "source": source,
        "cvssData": {
            "version": "3.1",
            "baseScore": score,
            "vectorString": VECTOR,
            "integrityImpact": "HIGH",
        },
    }


def make_payload(metrics=None, status="Analyzed"):
    if metrics is None:
        metrics = [make_metric()]

    return {
        "vulnerabilities": [
            {
                "cve": {
                    "id": CVE_ID,
                    "vulnStatus": status,
                    "descriptions": [{"lang": "en", "value": "Test vulnerability"}],
                    "metrics": {"cvssMetricV31": metrics},
                }
            }
        ]
    }


def make_record(score=7.0, impact="HIGH", status="Analyzed"):
    return {
        "description": "Test vulnerability",
        "vuln_status": status,
        "cvss_data": {
            "version": "3.1",
            "baseScore": score,
            "vectorString": VECTOR,
            "integrityImpact": impact,
        },
        "score_source": "test-source",
    }


# Перевірка threshold та правила варіанта
@pytest.mark.parametrize(
    "score, expected", [(6.9, "other"), (7.0, "review"), (7.1, "review")]
)
def test_build_report_threshold(score, expected):
    result = analysis.build_report(make_record(score=score), CVE_ID, VARIANT_NUMBER)

    assert result["decision"] == expected
    assert result["variant"] == VARIANT_NUMBER
    assert result["rule"] == {
        "threshold": 7.0,
        "field": "integrityImpact",
        "expected": "HIGH",
    }


def test_build_report_wrong_feature():
    result = analysis.build_report(
        make_record(score=9.8, impact="LOW"), CVE_ID, VARIANT_NUMBER
    )

    assert result["decision"] == "other"


# Перевірка відсутніх і відхилених записів
def test_not_found():
    result = analysis.extract_record({"vulnerabilities": []}, CVE_ID)

    assert result is None
    assert (
        analysis.build_report(None, CVE_ID, VARIANT_NUMBER)["decision"] == "not_found"
    )


def test_rejected():
    record = analysis.extract_record(make_payload(status="Rejected"), CVE_ID)

    assert (
        analysis.build_report(record, CVE_ID, VARIANT_NUMBER)["decision"] == "rejected"
    )


# Перевірка відсутніх полів
def test_missing_score():
    data = make_payload()
    cvss = data["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]
    del cvss["baseScore"]

    record = analysis.extract_record(data, CVE_ID)

    assert record["cvss_data"] is None
    assert (
        analysis.build_report(record, CVE_ID, VARIANT_NUMBER)["decision"]
        == "insufficient_data"
    )


def test_missing_required_field():
    record = make_record()
    del record["cvss_data"]["integrityImpact"]

    result = analysis.build_report(record, CVE_ID, VARIANT_NUMBER)

    assert result["decision"] == "insufficient_data"


# Перевірка неправильних значень
@pytest.mark.parametrize(
    "score", ["9.8", True, None, -0.1, 10.1, float("inf"), float("-inf"), float("nan")]
)
def test_invalid_base_score(score):
    data = make_payload()
    data["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"][
        "baseScore"
    ] = score

    with pytest.raises((ValueError, TypeError)):
        analysis.extract_record(make_payload(data), CVE_ID)


# Перевірка вибору оцінки CVSS
@pytest.mark.parametrize(
    "has_primary, expected_score, expected_source",
    [(True, 9.8, "primary"), (False, 6.1, "first")],
)
def test_metric_selection(has_primary, expected_score, expected_source):
    metrics = [
        make_metric(6.1, "Secondary", "first"),
        make_metric(
            9.8,
            "Primary" if has_primary else "Secondary",
            "primary" if has_primary else "second",
        ),
    ]

    result = analysis.extract_record(make_payload(metrics), CVE_ID)

    assert result["cvss_data"]["baseScore"] == expected_score
    assert result["score_source"] == expected_source
    assert result["description"] == "Test vulnerability"
