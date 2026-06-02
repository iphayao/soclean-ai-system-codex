from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.agents.llm_service import LLMService, create_llm_service
from app.rules.claim_rules import (
    BANNED_CLAIMS,
    calculate_review_score,
    detect_claim_risks,
    map_score_to_status,
    suggest_replacements,
)

DEFAULT_PLATFORMS = ["TikTok", "Facebook", "LINE"]
PRODUCT_FACTS = {
    "ply": "2 ชั้น",
    "sheets": "180 แผ่น",
    "bundle": "5 ห่อต่อแพ็ก",
    "carton": "50 แพ็กต่อกล่อง",
}
SAFE_CLAIMS = ["เนียนนุ่ม", "สะอาด", "ฝุ่นน้อย", "ไม่ฟุ้งง่าย"]
FORBIDDEN_CLAIMS = BANNED_CLAIMS
PASSING_REVIEW_STATUSES = {"ready_to_approve"}

CAMPAIGN_PLANNER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["plan"],
    "properties": {
        "plan": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["platform", "content_type", "pillar", "angle"],
                "properties": {
                    "platform": {"type": "string", "enum": DEFAULT_PLATFORMS},
                    "content_type": {"type": "string"},
                    "pillar": {"type": "string"},
                    "angle": {"type": "string"},
                },
            },
        }
    },
}

COPYWRITER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["items"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "platform",
                    "content_type",
                    "pillar",
                    "angle",
                    "hook",
                    "body",
                    "caption",
                    "cta",
                    "hashtags",
                ],
                "properties": {
                    "platform": {"type": "string", "enum": DEFAULT_PLATFORMS},
                    "content_type": {"type": "string"},
                    "pillar": {"type": "string"},
                    "angle": {"type": "string"},
                    "hook": {"type": "string"},
                    "body": {"type": "string"},
                    "caption": {"type": "string"},
                    "cta": {"type": "string"},
                    "hashtags": {"type": "array", "items": {"type": "string"}},
                },
            },
        }
    },
}

VISUAL_BRIEF_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["briefs"],
    "properties": {
        "briefs": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["platform", "brief", "shot_list", "text_overlay"],
                "properties": {
                    "platform": {"type": "string", "enum": DEFAULT_PLATFORMS},
                    "brief": {"type": "string"},
                    "shot_list": {"type": "array", "items": {"type": "string"}},
                    "text_overlay": {"type": "string"},
                },
            },
        }
    },
}

REVIEWER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "score", "issues", "revision_notes"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["ready_to_approve", "minor_revision_suggested", "revision_required", "reject"],
        },
        "score": {"type": "number"},
        "issues": {"type": "array", "items": {"type": "string"}},
        "revision_notes": {"type": "string"},
    },
}


class ContentFactoryState(TypedDict, total=False):
    campaign_id: str
    brand_id: str
    agent_run_id: str
    language: str
    platforms: list[str]
    product_facts: dict[str, str]
    safe_claims: list[str]
    forbidden_claims: list[str]
    brand_memory: dict[str, Any]
    customer_insights: list[str]
    content_strategy: dict[str, Any]
    campaign_plan: list[dict[str, Any]]
    generated_content: list[dict[str, Any]]
    visual_briefs: list[dict[str, Any]]
    review_passed: bool
    review_feedback: list[str]
    review_result: dict[str, Any]
    retry_count: int
    max_retries: int
    saved_content_item_ids: list[str]
    db: Session
    llm_service: LLMService
    step_index: int
    force_initial_review_failure: bool
    force_always_fail: bool


def _state_without_db(state: ContentFactoryState) -> dict[str, Any]:
    return {key: value for key, value in state.items() if key not in {"db", "llm_service"}}


def _llm(state: ContentFactoryState) -> LLMService:
    service = state.get("llm_service")
    if service is None:
        service = create_llm_service()
    return service


def _llm_context(state: ContentFactoryState) -> dict[str, Any]:
    return {
        "db": state.get("db"),
        "campaign_id": state.get("campaign_id"),
        "agent_run_id": state.get("agent_run_id"),
    }


def _record_step(state: ContentFactoryState, step_name: str, updates: dict[str, Any]) -> dict[str, Any]:
    step_index = state.get("step_index", 0) + 1
    db = state.get("db")
    agent_run_id = state.get("agent_run_id")

    if db is not None and agent_run_id:
        step = models.AgentRunStep(
            agent_run_id=agent_run_id,
            step_order=step_index,
            step_name=step_name,
            status="completed",
            input_metadata={
                "campaign_id": state.get("campaign_id"),
                "retry_count": state.get("retry_count", 0),
            },
            output_metadata=_state_without_db(ContentFactoryState(**updates)),
        )
        db.add(step)
        db.commit()

    return {**updates, "step_index": step_index}


def _get_campaign_context(state: ContentFactoryState) -> tuple[models.Campaign | None, models.Brand | None]:
    db = state.get("db")
    campaign_id = state.get("campaign_id")
    if db is None or not campaign_id:
        return None, None

    campaign = db.get(models.Campaign, campaign_id)
    brand = db.get(models.Brand, campaign.brand_id) if campaign is not None else None
    return campaign, brand


def load_brand_memory(state: ContentFactoryState) -> dict[str, Any]:
    campaign, brand = _get_campaign_context(state)
    products: list[models.Product] = []
    db = state.get("db")
    if db is not None and campaign is not None:
        products = list(db.scalars(select(models.Product).where(models.Product.brand_id == campaign.brand_id)).all())

    brand_memory = {
        "brand_name": brand.name if brand else "SoClean",
        "voice": brand.voice if brand and brand.voice else "ภาษาไทยที่ชัดเจน อบอุ่น และน่าเชื่อถือ",
        "compliance_notes": brand.compliance_notes if brand and brand.compliance_notes else "หลีกเลี่ยงคำกล่าวอ้างเกินจริง",
        "campaign_objective": campaign.objective if campaign else "สร้างคอนเทนต์ภาษาไทยสำหรับโซเชียล",
        "product_names": [product.name for product in products] or ["SoClean Tissue"],
    }
    return _record_step(state, "load_brand_memory", {"brand_memory": brand_memory})


def generate_customer_insights(state: ContentFactoryState) -> dict[str, Any]:
    insights = [
        "ผู้ซื้อให้ความสำคัญกับทิชชู่ที่ใช้ได้ทุกวันและสัมผัสนุ่ม",
        "ข้อความควรสื่อเรื่องความสะอาด ฝุ่นน้อย และใช้งานง่ายในบ้านหรือร้านค้า",
        "คอนเทนต์ควรสั้น กระชับ และเหมาะกับ TikTok, Facebook, LINE",
    ]
    return _record_step(state, "generate_customer_insights", {"customer_insights": insights})


def generate_content_strategy(state: ContentFactoryState) -> dict[str, Any]:
    strategy = {
        "language": state.get("language", "th"),
        "message": "ทิชชู่ SoClean เนียนนุ่ม สะอาด ฝุ่นน้อย ไม่ฟุ้งง่าย สำหรับการใช้งานทุกวัน",
        "proof_points": list(PRODUCT_FACTS.values()),
        "safe_claims": state.get("safe_claims", SAFE_CLAIMS),
        "forbidden_claims": state.get("forbidden_claims", FORBIDDEN_CLAIMS),
    }
    return _record_step(state, "generate_content_strategy", {"content_strategy": strategy})


def generate_campaign_plan(state: ContentFactoryState) -> dict[str, Any]:
    result = _llm(state).generate_json(
        agent_name="campaign_planner",
        variables={
            "language": state.get("language", "th"),
            "platforms": state.get("platforms", DEFAULT_PLATFORMS),
            "brand_memory": state.get("brand_memory", {}),
            "customer_insights": state.get("customer_insights", []),
            "content_strategy": state.get("content_strategy", {}),
            "product_facts": state.get("product_facts", PRODUCT_FACTS),
            "safe_claims": state.get("safe_claims", SAFE_CLAIMS),
            "forbidden_claims": state.get("forbidden_claims", FORBIDDEN_CLAIMS),
        },
        response_schema=CAMPAIGN_PLANNER_SCHEMA,
        **_llm_context(state),
    )
    plan = result.data.get("plan", [])
    return _record_step(state, "generate_campaign_plan", {"campaign_plan": plan})


def generate_content(state: ContentFactoryState) -> dict[str, Any]:
    result = _llm(state).generate_json(
        agent_name="copywriter",
        variables={
            "language": state.get("language", "th"),
            "campaign_plan": state.get("campaign_plan", []),
            "brand_memory": state.get("brand_memory", {}),
            "content_strategy": state.get("content_strategy", {}),
            "product_facts": state.get("product_facts", PRODUCT_FACTS),
            "safe_claims": state.get("safe_claims", SAFE_CLAIMS),
            "forbidden_claims": state.get("forbidden_claims", FORBIDDEN_CLAIMS),
            "retry_count": state.get("retry_count", 0),
            "force_initial_review_failure": state.get("force_initial_review_failure", False),
        },
        response_schema=COPYWRITER_SCHEMA,
        **_llm_context(state),
    )

    generated = []
    for item in result.data.get("items", []):
        platform = item["platform"]
        generated.append(
            {
                "title": item["hook"],
                "channel": platform,
                "format": item["content_type"],
                "body": item["body"],
                "metadata": {
                    "language": state.get("language", "th"),
                    "angle": item["angle"],
                    "pillar": item["pillar"],
                    "hook": item["hook"],
                    "caption": item["caption"],
                    "cta": item["cta"],
                    "hashtags": item["hashtags"],
                    "retry_count": state.get("retry_count", 0),
                },
            }
        )

    return _record_step(state, "generate_content", {"generated_content": generated})


def generate_visual_briefs(state: ContentFactoryState) -> dict[str, Any]:
    result = _llm(state).generate_json(
        agent_name="visual_brief",
        variables={
            "language": state.get("language", "th"),
            "generated_content": state.get("generated_content", []),
            "brand_memory": state.get("brand_memory", {}),
            "safe_claims": state.get("safe_claims", SAFE_CLAIMS),
            "forbidden_claims": state.get("forbidden_claims", FORBIDDEN_CLAIMS),
        },
        response_schema=VISUAL_BRIEF_SCHEMA,
        **_llm_context(state),
    )
    briefs = [
        {
            "channel": item["platform"],
            "brief": item["brief"],
            "shot_list": item["shot_list"],
            "text_overlay": item["text_overlay"],
        }
        for item in result.data.get("briefs", [])
    ]
    return _record_step(state, "generate_visual_briefs", {"visual_briefs": briefs})


def review_content(state: ContentFactoryState) -> dict[str, Any]:
    generated_content = state.get("generated_content", [])
    rule_score = calculate_review_score(generated_content)
    rule_status = map_score_to_status(rule_score)
    content_blob = " ".join(
        [
            item.get("body", "")
            + " "
            + item.get("metadata", {}).get("caption", "")
            + " "
            + item.get("metadata", {}).get("hook", "")
            + " "
            + item.get("metadata", {}).get("cta", "")
            for item in generated_content
        ]
    )
    claim_risks = detect_claim_risks(content_blob)
    replacement_suggestions = suggest_replacements(content_blob)

    result = _llm(state).generate_json(
        agent_name="reviewer",
        variables={
            "language": state.get("language", "th"),
            "generated_content": generated_content,
            "visual_briefs": state.get("visual_briefs", []),
            "product_facts": state.get("product_facts", PRODUCT_FACTS),
            "safe_claims": state.get("safe_claims", SAFE_CLAIMS),
            "forbidden_claims": state.get("forbidden_claims", FORBIDDEN_CLAIMS),
            "deterministic_rule_score": rule_score,
            "deterministic_rule_status": rule_status,
            "claim_risks": claim_risks,
            "replacement_suggestions": replacement_suggestions,
            "force_always_fail": state.get("force_always_fail", False),
        },
        response_schema=REVIEWER_SCHEMA,
        **_llm_context(state),
    )

    review = result.data
    feedback: list[str] = list(review.get("issues", []))
    for risk in claim_risks:
        message = risk["message"]
        if message not in feedback:
            feedback.append(message)

    if state.get("force_always_fail", False):
        message = "Forced deterministic review failure"
        if message not in feedback:
            feedback.append(message)

    status = review.get("status", "revision_required")
    if rule_status != "ready_to_approve":
        status = rule_status
    elif claim_risks and status in PASSING_REVIEW_STATUSES:
        status = "revision_required"
    score = min(int(review.get("score", 0)), rule_score)
    review_passed = status in PASSING_REVIEW_STATUSES and not feedback and not claim_risks
    updates = {
        "review_passed": review_passed,
        "review_feedback": feedback or [review.get("revision_notes") or "ผ่านการตรวจคำกล่าวอ้างเบื้องต้น"],
        "review_result": {
            "status": status,
            "score": score,
            "issues": feedback,
            "revision_notes": review.get("revision_notes", ""),
            "rule_engine": {
                "score": rule_score,
                "status": rule_status,
                "claim_risks": claim_risks,
                "replacement_suggestions": replacement_suggestions,
            },
        },
    }
    return _record_step(state, "review_content", updates)


def rewrite_content(state: ContentFactoryState) -> dict[str, Any]:
    replacements = {
        "ไร้ฝุ่น 100%": "ฝุ่นน้อย",
        "ไม่ก่อภูมิแพ้": "เหมาะสำหรับใช้ในชีวิตประจำวัน",
        "ฆ่าเชื้อโรค": "",
        "ปลอดภัยที่สุด": "สะอาด น่าใช้",
        "medical grade": "",
        "antibacterial": "",
        "hypoallergenic": "เหมาะสำหรับใช้ในชีวิตประจำวัน",
    }
    rewritten = []
    for item in state.get("generated_content", []):
        body = item.get("body", "")
        for forbidden, safe in replacements.items():
            body = body.replace(forbidden, safe)
        rewritten.append(
            {
                **item,
                "body": f"{body} ปรับข้อความให้ใช้คำกล่าวอ้างที่ปลอดภัย",
                "metadata": {**item.get("metadata", {}), "rewritten": True},
            }
        )

    return _record_step(
        state,
        "rewrite_content",
        {
            "generated_content": rewritten,
            "retry_count": state.get("retry_count", 0) + 1,
        },
    )


def save_content(state: ContentFactoryState) -> dict[str, Any]:
    db = state.get("db")
    campaign_id = state.get("campaign_id")
    saved_ids: list[str] = []

    if db is not None and campaign_id:
        status = "in_review" if state.get("review_passed", False) else "draft"
        for item in state.get("generated_content", []):
            content_item = models.ContentItem(
                campaign_id=campaign_id,
                title=item["title"],
                channel=item["channel"],
                format=item["format"],
                status=status,
                body=item["body"],
                item_metadata={
                    **item.get("metadata", {}),
                    "agent_run_id": state.get("agent_run_id"),
                    "visual_brief": next(
                        (
                            brief["brief"]
                            for brief in state.get("visual_briefs", [])
                            if brief["channel"] == item["channel"]
                        ),
                        None,
                    ),
                    "review_feedback": state.get("review_feedback", []),
                    "review_result": state.get("review_result", {}),
                },
            )
            db.add(content_item)
            db.flush()
            saved_ids.append(content_item.id)
        db.commit()

    return _record_step(state, "save_content", {"saved_content_item_ids": saved_ids})


def should_rewrite(state: ContentFactoryState) -> str:
    if state.get("review_passed", False):
        return "save"
    if state.get("retry_count", 0) < state.get("max_retries", 2):
        return "rewrite"
    return "save"


def build_content_factory_graph():
    graph = StateGraph(ContentFactoryState)
    graph.add_node("load_brand_memory", load_brand_memory)
    graph.add_node("generate_customer_insights", generate_customer_insights)
    graph.add_node("generate_content_strategy", generate_content_strategy)
    graph.add_node("generate_campaign_plan", generate_campaign_plan)
    graph.add_node("generate_content", generate_content)
    graph.add_node("generate_visual_briefs", generate_visual_briefs)
    graph.add_node("review_content", review_content)
    graph.add_node("rewrite_content", rewrite_content)
    graph.add_node("save_content", save_content)

    graph.add_edge(START, "load_brand_memory")
    graph.add_edge("load_brand_memory", "generate_customer_insights")
    graph.add_edge("generate_customer_insights", "generate_content_strategy")
    graph.add_edge("generate_content_strategy", "generate_campaign_plan")
    graph.add_edge("generate_campaign_plan", "generate_content")
    graph.add_edge("generate_content", "generate_visual_briefs")
    graph.add_edge("generate_visual_briefs", "review_content")
    graph.add_conditional_edges("review_content", should_rewrite, {"rewrite": "rewrite_content", "save": "save_content"})
    graph.add_edge("rewrite_content", "generate_visual_briefs")
    graph.add_edge("save_content", END)
    return graph.compile()


content_factory_graph = build_content_factory_graph()


def initial_state(
    campaign_id: str,
    request: schemas.GenerateContentRequest | None = None,
    **overrides: Any,
) -> ContentFactoryState:
    request = request or schemas.GenerateContentRequest()
    return ContentFactoryState(
        campaign_id=campaign_id,
        language=request.language or "th",
        platforms=request.platforms or DEFAULT_PLATFORMS,
        product_facts=PRODUCT_FACTS,
        safe_claims=SAFE_CLAIMS,
        forbidden_claims=FORBIDDEN_CLAIMS,
        retry_count=0,
        max_retries=request.max_retries,
        saved_content_item_ids=[],
        force_initial_review_failure=request.force_initial_review_failure,
        llm_service=overrides.pop("llm_service", create_llm_service()),
        **overrides,
    )


def run_content_factory_graph(state: ContentFactoryState) -> ContentFactoryState:
    return content_factory_graph.invoke(state)


def run_content_factory(
    db: Session,
    campaign_id: str,
    request: schemas.GenerateContentRequest,
) -> schemas.GenerateContentResponse:
    agent_run = models.AgentRun(
        campaign_id=campaign_id,
        workflow_name="content_factory",
        status="running",
        run_metadata={
            "language": request.language,
            "platforms": request.platforms,
            "max_retries": request.max_retries,
        },
    )
    db.add(agent_run)
    db.commit()
    db.refresh(agent_run)

    try:
        final_state = run_content_factory_graph(
            initial_state(campaign_id, request, db=db, agent_run_id=agent_run.id)
        )
        agent_run.status = "completed"
        agent_run.retry_count = final_state.get("retry_count", 0)
        agent_run.output_metadata = {
            "review_passed": final_state.get("review_passed", False),
            "review_feedback": final_state.get("review_feedback", []),
            "content_item_ids": final_state.get("saved_content_item_ids", []),
        }
        db.commit()
    except Exception as exc:
        agent_run.status = "failed"
        agent_run.output_metadata = {"error": str(exc)}
        db.commit()
        raise

    content_items = list(
        db.scalars(
            select(models.ContentItem).where(
                models.ContentItem.id.in_(final_state.get("saved_content_item_ids", []))
            )
        ).all()
    )
    return schemas.GenerateContentResponse(
        agent_run_id=agent_run.id,
        campaign_id=campaign_id,
        status=agent_run.status,
        retry_count=agent_run.retry_count,
        review_passed=final_state.get("review_passed", False),
        content_item_ids=final_state.get("saved_content_item_ids", []),
        content_items=content_items,
    )
