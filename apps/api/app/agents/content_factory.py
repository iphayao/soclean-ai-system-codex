from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas

DEFAULT_PLATFORMS = ["TikTok", "Facebook", "LINE"]
PRODUCT_FACTS = {
    "ply": "2 ชั้น",
    "sheets": "180 แผ่น",
    "bundle": "5 ห่อต่อแพ็ก",
    "carton": "50 แพ็กต่อกล่อง",
}
SAFE_CLAIMS = ["เนียนนุ่ม", "สะอาด", "ฝุ่นน้อย", "ไม่ฟุ้งง่าย"]
FORBIDDEN_CLAIMS = ["ไร้ฝุ่น 100%", "ไม่ก่อภูมิแพ้", "ฆ่าเชื้อโรค", "ปลอดภัยที่สุด"]


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
    retry_count: int
    max_retries: int
    saved_content_item_ids: list[str]
    db: Session
    step_index: int
    force_initial_review_failure: bool
    force_always_fail: bool


def _state_without_db(state: ContentFactoryState) -> dict[str, Any]:
    return {key: value for key, value in state.items() if key != "db"}


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
    platforms = state.get("platforms", DEFAULT_PLATFORMS)
    plan = [
        {
            "platform": platform,
            "format": "short_video" if platform == "TikTok" else "social_post",
            "angle": f"แนะนำจุดเด่น SoClean สำหรับ {platform}",
        }
        for platform in platforms
    ]
    return _record_step(state, "generate_campaign_plan", {"campaign_plan": plan})


def generate_content(state: ContentFactoryState) -> dict[str, Any]:
    plan = state.get("campaign_plan", [])
    fact_line = " ".join(PRODUCT_FACTS.values())
    safe_line = " ".join(state.get("safe_claims", SAFE_CLAIMS))
    inject_forbidden = state.get("force_initial_review_failure", False) and state.get("retry_count", 0) == 0

    generated = []
    for item in plan:
        platform = item["platform"]
        body = (
            f"SoClean ทิชชู่ {fact_line} ให้สัมผัส{safe_line} "
            f"เหมาะกับการใช้งานประจำวันบน {platform}"
        )
        if inject_forbidden:
            body = f"{body} ไร้ฝุ่น 100%"
        generated.append(
            {
                "title": f"SoClean สำหรับ {platform}",
                "channel": platform,
                "format": item["format"],
                "body": body,
                "metadata": {
                    "language": state.get("language", "th"),
                    "angle": item["angle"],
                    "retry_count": state.get("retry_count", 0),
                },
            }
        )

    return _record_step(state, "generate_content", {"generated_content": generated})


def generate_visual_briefs(state: ContentFactoryState) -> dict[str, Any]:
    briefs = [
        {
            "channel": item["channel"],
            "brief": "ภาพแพ็กสินค้า SoClean บนพื้นหลังสะอาด พร้อมข้อความสั้นเรื่องเนียนนุ่มและฝุ่นน้อย",
        }
        for item in state.get("generated_content", [])
    ]
    return _record_step(state, "generate_visual_briefs", {"visual_briefs": briefs})


def review_content(state: ContentFactoryState) -> dict[str, Any]:
    feedback: list[str] = []
    forbidden_claims = state.get("forbidden_claims", FORBIDDEN_CLAIMS)

    for item in state.get("generated_content", []):
        for claim in forbidden_claims:
            if claim in item.get("body", ""):
                feedback.append(f"{item['channel']}: พบคำกล่าวอ้างต้องห้าม '{claim}'")

    if state.get("force_always_fail", False):
        feedback.append("Forced deterministic review failure")

    review_passed = not feedback
    updates = {
        "review_passed": review_passed,
        "review_feedback": feedback or ["ผ่านการตรวจคำกล่าวอ้างเบื้องต้น"],
    }
    return _record_step(state, "review_content", updates)


def rewrite_content(state: ContentFactoryState) -> dict[str, Any]:
    replacements = {
        "ไร้ฝุ่น 100%": "ฝุ่นน้อย",
        "ไม่ก่อภูมิแพ้": "อ่อนโยนต่อการใช้งานทั่วไป",
        "ฆ่าเชื้อโรค": "สะอาด",
        "ปลอดภัยที่สุด": "เหมาะกับการใช้งานประจำวัน",
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
