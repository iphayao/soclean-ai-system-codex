from __future__ import annotations

import hashlib
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


DEFAULT_MODEL = "gpt-4o-mini"


@dataclass
class LLMResult:
    data: dict[str, Any]
    provider: str
    model_name: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    raw_response_metadata: dict[str, Any] | None = None
    prompt_version_id: str | None = None


class LLMService(ABC):
    @abstractmethod
    def generate_json(
        self,
        *,
        agent_name: str,
        variables: dict[str, Any],
        response_schema: dict[str, Any],
        db: Session | None = None,
        campaign_id: str | None = None,
        agent_run_id: str | None = None,
    ) -> LLMResult:
        raise NotImplementedError


def _prompt_dir() -> Path:
    env_dir = os.getenv("PROMPTS_DIR")
    if env_dir:
        return Path(env_dir)

    candidates = [
        Path.cwd() / "prompts",
        Path(__file__).resolve().parents[2] / "prompts",
        Path(__file__).resolve().parents[4] / "prompts",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def load_prompt(agent_name: str) -> str:
    prompt_path = _prompt_dir() / f"{agent_name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found for agent '{agent_name}': {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def render_prompt(prompt_template: str, variables: dict[str, Any]) -> str:
    rendered = prompt_template
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", json.dumps(value, ensure_ascii=False, indent=2))
    return rendered


def get_or_create_prompt_version(db: Session | None, agent_name: str, prompt_text: str) -> str | None:
    if db is None:
        return None

    content_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    existing = db.scalar(
        select(models.PromptVersion).where(
            models.PromptVersion.agent_name == agent_name,
            models.PromptVersion.content_hash == content_hash,
        )
    )
    if existing is not None:
        return existing.id

    prompt_version = models.PromptVersion(
        agent_name=agent_name,
        version="v1",
        content_hash=content_hash,
        prompt_text=prompt_text,
    )
    db.add(prompt_version)
    db.commit()
    db.refresh(prompt_version)
    return prompt_version.id


def log_llm_usage(
    db: Session | None,
    *,
    result: LLMResult,
    agent_name: str,
    campaign_id: str | None,
    agent_run_id: str | None,
) -> None:
    if db is None:
        return

    db.add(
        models.LLMUsageLog(
            agent_run_id=agent_run_id,
            campaign_id=campaign_id,
            prompt_version_id=result.prompt_version_id,
            agent_name=agent_name,
            provider=result.provider,
            model_name=result.model_name,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
            raw_response_metadata=result.raw_response_metadata or {},
        )
    )
    db.commit()


def parse_json_object(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response was not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("LLM response must be a JSON object")
    return parsed


class BaseLLMService(LLMService):
    provider = "base"
    model_name = "base"

    def _prepare_prompt(self, db: Session | None, agent_name: str, variables: dict[str, Any]) -> tuple[str, str | None]:
        prompt_template = load_prompt(agent_name)
        rendered_prompt = render_prompt(prompt_template, variables)
        prompt_version_id = get_or_create_prompt_version(db, agent_name, prompt_template)
        return rendered_prompt, prompt_version_id

    def _finalize(
        self,
        db: Session | None,
        *,
        result: LLMResult,
        agent_name: str,
        campaign_id: str | None,
        agent_run_id: str | None,
    ) -> LLMResult:
        log_llm_usage(
            db,
            result=result,
            agent_name=agent_name,
            campaign_id=campaign_id,
            agent_run_id=agent_run_id,
        )
        return result


class DeterministicMockLLMService(BaseLLMService):
    provider = "mock"
    model_name = "deterministic-mock"

    def generate_json(
        self,
        *,
        agent_name: str,
        variables: dict[str, Any],
        response_schema: dict[str, Any],
        db: Session | None = None,
        campaign_id: str | None = None,
        agent_run_id: str | None = None,
    ) -> LLMResult:
        rendered_prompt, prompt_version_id = self._prepare_prompt(db, agent_name, variables)
        data = self._mock_response(agent_name, variables)
        result = LLMResult(
            data=data,
            provider=self.provider,
            model_name=self.model_name,
            prompt_tokens=len(rendered_prompt.split()),
            completion_tokens=len(json.dumps(data, ensure_ascii=False).split()),
            total_tokens=len(rendered_prompt.split()) + len(json.dumps(data, ensure_ascii=False).split()),
            raw_response_metadata={"mode": "deterministic"},
            prompt_version_id=prompt_version_id,
        )
        return self._finalize(
            db,
            result=result,
            agent_name=agent_name,
            campaign_id=campaign_id,
            agent_run_id=agent_run_id,
        )

    def _mock_response(self, agent_name: str, variables: dict[str, Any]) -> dict[str, Any]:
        if agent_name == "campaign_planner":
            return {"plan": self._campaign_plan(variables)}
        if agent_name == "copywriter":
            return {"items": self._copy_items(variables)}
        if agent_name == "visual_brief":
            return {"briefs": self._visual_briefs(variables)}
        if agent_name == "reviewer":
            return self._review(variables)
        raise ValueError(f"Unsupported mock agent: {agent_name}")

    def _campaign_plan(self, variables: dict[str, Any]) -> list[dict[str, Any]]:
        platforms = variables.get("platforms") or ["TikTok", "Facebook", "LINE"]
        return [
            {
                "platform": platform,
                "content_type": "short_video" if platform == "TikTok" else "social_post",
                "pillar": "product_education",
                "angle": f"เล่าให้เห็นว่าทิชชู่ SoClean ใช้ง่ายและเหมาะกับ {platform}",
            }
            for platform in platforms
        ]

    def _copy_items(self, variables: dict[str, Any]) -> list[dict[str, Any]]:
        plan = variables.get("campaign_plan") or self._campaign_plan(variables)
        product_facts = variables.get("product_facts") or {}
        fact_line = " ".join(product_facts.values()) or "2 ชั้น 180 แผ่น 5 ห่อต่อแพ็ก 50 แพ็กต่อกล่อง"
        inject_forbidden = variables.get("force_initial_review_failure", False) and variables.get("retry_count", 0) == 0
        items = []
        for plan_item in plan:
            platform = plan_item["platform"]
            body = (
                f"SoClean ทิชชู่ {fact_line} เนียนนุ่ม สะอาด ฝุ่นน้อย ไม่ฟุ้งง่าย "
                f"เหมาะกับบ้าน ร้านค้า และการใช้งานทุกวัน"
            )
            if inject_forbidden:
                body = f"{body} ไร้ฝุ่น 100%"
            items.append(
                {
                    "platform": platform,
                    "content_type": plan_item.get("content_type", plan_item.get("format", "social_post")),
                    "pillar": plan_item.get("pillar", "product_education"),
                    "angle": plan_item.get("angle", f"จุดเด่น SoClean สำหรับ {platform}"),
                    "hook": "ทิชชู่ที่หยิบใช้แล้วรู้สึกต่างตั้งแต่สัมผัสแรก",
                    "body": body,
                    "caption": "เลือก SoClean สำหรับความสะอาดที่สัมผัสได้ในทุกวัน",
                    "cta": "สั่งซื้อหรือสอบถามรายละเอียดได้เลย",
                    "hashtags": ["#SoClean", "#ทิชชู่", "#เนียนนุ่ม", "#ฝุ่นน้อย"],
                }
            )
        return items

    def _visual_briefs(self, variables: dict[str, Any]) -> list[dict[str, Any]]:
        items = variables.get("generated_content") or []
        return [
            {
                "platform": item["channel"],
                "brief": "ภาพแพ็กสินค้า SoClean วางในพื้นที่สะอาด สว่าง พร้อมเน้นข้อความเนียนนุ่มและฝุ่นน้อย",
                "shot_list": ["แพ็กสินค้า", "มือหยิบใช้งาน", "พื้นที่สะอาดในบ้านหรือร้าน"],
                "text_overlay": "เนียนนุ่ม สะอาด ฝุ่นน้อย",
            }
            for item in items
        ]

    def _review(self, variables: dict[str, Any]) -> dict[str, Any]:
        forbidden_claims = variables.get("forbidden_claims") or []
        content_blob = json.dumps(variables.get("generated_content") or [], ensure_ascii=False)
        issues = [f"พบคำกล่าวอ้างต้องห้าม: {claim}" for claim in forbidden_claims if claim in content_blob]
        if variables.get("force_always_fail", False):
            issues.append("Forced deterministic review failure")
        if issues:
            return {
                "status": "revision_required",
                "score": 45,
                "issues": issues,
                "revision_notes": "ปรับคำกล่าวอ้างให้ปลอดภัยและอิงข้อเท็จจริงของสินค้า",
            }
        return {
            "status": "ready_to_approve",
            "score": 92,
            "issues": [],
            "revision_notes": "",
        }


class OpenAICompatibleLLMService(BaseLLMService):
    provider = "openai-compatible"

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.timeout = timeout

    def generate_json(
        self,
        *,
        agent_name: str,
        variables: dict[str, Any],
        response_schema: dict[str, Any],
        db: Session | None = None,
        campaign_id: str | None = None,
        agent_run_id: str | None = None,
    ) -> LLMResult:
        rendered_prompt, prompt_version_id = self._prepare_prompt(db, agent_name, variables)
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": rendered_prompt},
                {"role": "user", "content": "Return only valid JSON that matches the required schema."},
            ],
            "temperature": 0.2,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": f"{agent_name}_output",
                    "strict": True,
                    "schema": response_schema,
                },
            },
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        response_body = response.json()
        content = response_body["choices"][0]["message"]["content"]
        data = parse_json_object(content)
        usage = response_body.get("usage", {})
        result = LLMResult(
            data=data,
            provider=self.provider,
            model_name=response_body.get("model", self.model_name),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            raw_response_metadata={
                "id": response_body.get("id"),
                "finish_reason": response_body.get("choices", [{}])[0].get("finish_reason"),
            },
            prompt_version_id=prompt_version_id,
        )
        return self._finalize(
            db,
            result=result,
            agent_name=agent_name,
            campaign_id=campaign_id,
            agent_run_id=agent_run_id,
        )


def create_llm_service() -> LLMService:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return DeterministicMockLLMService()
    return OpenAICompatibleLLMService(api_key=api_key)
