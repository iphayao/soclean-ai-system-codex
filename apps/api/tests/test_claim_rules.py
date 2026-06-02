from app.rules.claim_rules import (
    calculate_review_score,
    detect_claim_risks,
    map_score_to_status,
    suggest_replacements,
)


def test_banned_claims_are_detected() -> None:
    risks = detect_claim_risks("SoClean ไร้ฝุ่น 100% และเป็น medical grade")

    assert {risk["claim"] for risk in risks} == {"ไร้ฝุ่น 100%", "medical grade"}
    assert any(risk["category"] == "unsupported_absolute_claim" for risk in risks)
    assert any(risk["category"] == "banned_medical_or_safety_claim" for risk in risks)


def test_safe_claims_pass() -> None:
    content = {
        "body": "SoClean ทิชชู่ 2 ชั้น 180 แผ่น เนียนนุ่ม สะอาด ฝุ่นน้อย ไม่ฟุ้งง่าย",
        "metadata": {"cta": "สอบถามรายละเอียดและสั่งซื้อได้เลย"},
    }

    assert detect_claim_risks(content["body"]) == []
    assert calculate_review_score(content) == 100
    assert map_score_to_status(calculate_review_score(content)) == "ready_to_approve"


def test_risky_content_cannot_be_approved_automatically() -> None:
    content = {
        "body": "SoClean ทิชชู่ 2 ชั้น 180 แผ่น ฆ่าเชื้อโรค ปลอดภัยที่สุด",
        "metadata": {"cta": "สั่งซื้อได้เลย"},
    }

    score = calculate_review_score(content)

    assert score < 60
    assert map_score_to_status(score) == "reject"


def test_replacements_are_suggested() -> None:
    suggestions = suggest_replacements("SoClean ไร้ฝุ่น 100% ไม่ก่อภูมิแพ้ ฆ่าเชื้อโรค")

    by_claim = {item["claim"]: item for item in suggestions}
    assert by_claim["ไร้ฝุ่น 100%"]["replacements"] == ["ฝุ่นน้อย", "ไม่ฟุ้งง่าย"]
    assert by_claim["ไม่ก่อภูมิแพ้"]["replacements"] == ["เหมาะสำหรับใช้ในชีวิตประจำวัน"]
    assert by_claim["ฆ่าเชื้อโรค"]["action"] == "remove"
