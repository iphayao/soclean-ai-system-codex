from __future__ import annotations

from typing import Any, Literal, TypedDict


BANNED_CLAIMS = [
    "ไร้ฝุ่น 100%",
    "ไม่ก่อภูมิแพ้",
    "ฆ่าเชื้อโรค",
    "ปลอดภัยที่สุด",
    "medical grade",
    "antibacterial",
    "hypoallergenic",
]

PREFERRED_REPLACEMENTS = {
    "ไร้ฝุ่น 100%": ["ฝุ่นน้อย", "ไม่ฟุ้งง่าย"],
    "ไม่ก่อภูมิแพ้": ["เหมาะสำหรับใช้ในชีวิตประจำวัน"],
    "ฆ่าเชื้อโรค": [],
    "ปลอดภัยที่สุด": ["สะอาด น่าใช้"],
    "medical grade": [],
    "antibacterial": [],
    "hypoallergenic": ["เหมาะสำหรับใช้ในชีวิตประจำวัน"],
}

MEDICAL_OR_SAFETY_CLAIMS = {
    "ไม่ก่อภูมิแพ้",
    "ฆ่าเชื้อโรค",
    "ปลอดภัยที่สุด",
    "medical grade",
    "antibacterial",
    "hypoallergenic",
}

UNSUPPORTED_ABSOLUTE_CLAIMS = {"ไร้ฝุ่น 100%"}

PRODUCT_FACT_TERMS = ["2 ชั้น", "180 แผ่น", "5 ห่อ", "5 แพ็ก", "50 แพ็ก", "50 กล่อง"]
CTA_TERMS = ["สั่งซื้อ", "สอบถาม", "ทัก", "ดูรายละเอียด", "ติดต่อ", "แอดไลน์", "คลิก"]
THAI_PLACEHOLDERS = ["...", "lorem", "placeholder", "TODO", "ใส่ข้อความ", "ตัวอย่างข้อความ"]

ReviewStatus = Literal["ready_to_approve", "minor_revision_suggested", "revision_required", "reject"]


class ClaimRisk(TypedDict):
    claim: str
    category: str
    deduction: int
    message: str


class ReplacementSuggestion(TypedDict):
    claim: str
    replacements: list[str]
    action: str


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        parts: list[str] = []
        for key in ("hook", "body", "caption", "cta", "title"):
            value = content.get(key)
            if isinstance(value, str):
                parts.append(value)
        metadata = content.get("metadata")
        if isinstance(metadata, dict):
            for key in ("hook", "caption", "cta", "angle", "pillar"):
                value = metadata.get(key)
                if isinstance(value, str):
                    parts.append(value)
        return " ".join(parts)
    if isinstance(content, list):
        return " ".join(_content_text(item) for item in content)
    return str(content)


def _contains(text: str, needle: str) -> bool:
    return needle.casefold() in text.casefold()


def detect_claim_risks(text: str) -> list[ClaimRisk]:
    risks: list[ClaimRisk] = []
    for claim in BANNED_CLAIMS:
        if not _contains(text, claim):
            continue
        if claim in MEDICAL_OR_SAFETY_CLAIMS:
            risks.append(
                {
                    "claim": claim,
                    "category": "banned_medical_or_safety_claim",
                    "deduction": 30,
                    "message": f"พบคำกล่าวอ้างด้านการแพทย์หรือความปลอดภัยที่ห้ามใช้: {claim}",
                }
            )
        elif claim in UNSUPPORTED_ABSOLUTE_CLAIMS:
            risks.append(
                {
                    "claim": claim,
                    "category": "unsupported_absolute_claim",
                    "deduction": 20,
                    "message": f"พบคำกล่าวอ้างแบบเด็ดขาดที่ยังไม่มีหลักฐานรองรับ: {claim}",
                }
            )
    return risks


def suggest_replacements(text: str) -> list[ReplacementSuggestion]:
    suggestions: list[ReplacementSuggestion] = []
    for claim, replacements in PREFERRED_REPLACEMENTS.items():
        if not _contains(text, claim):
            continue
        suggestions.append(
            {
                "claim": claim,
                "replacements": replacements,
                "action": "remove" if not replacements else "replace",
            }
        )
    return suggestions


def _has_cta(text: str) -> bool:
    return any(_contains(text, term) for term in CTA_TERMS)


def _has_product_fact(text: str) -> bool:
    return any(_contains(text, term) for term in PRODUCT_FACT_TERMS)


def _has_weak_thai_quality(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 20:
        return True
    if any(_contains(stripped, placeholder) for placeholder in THAI_PLACEHOLDERS):
        return True
    thai_chars = sum(1 for char in stripped if "\u0e00" <= char <= "\u0e7f")
    alpha_chars = sum(1 for char in stripped if char.isalpha())
    return alpha_chars > 0 and thai_chars / alpha_chars < 0.25


def calculate_review_score(content: Any) -> int:
    text = _content_text(content)
    score = 100
    for risk in detect_claim_risks(text):
        score -= risk["deduction"]
    if not _has_cta(text):
        score -= 10
    if not _has_product_fact(text):
        score -= 10
    if _has_weak_thai_quality(text):
        score -= 10
    return max(0, min(100, score))


def map_score_to_status(score: int) -> ReviewStatus:
    if score >= 90:
        return "ready_to_approve"
    if score >= 75:
        return "minor_revision_suggested"
    if score >= 60:
        return "revision_required"
    return "reject"
