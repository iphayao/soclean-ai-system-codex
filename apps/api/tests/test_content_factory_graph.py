from app import schemas
from app.agents.content_factory import FORBIDDEN_CLAIMS, initial_state, run_content_factory_graph
from app.agents.llm_service import DeterministicMockLLMService


class RiskyPassingReviewMockLLMService(DeterministicMockLLMService):
    def _mock_response(self, agent_name: str, variables: dict) -> dict:
        if agent_name == "copywriter":
            return {
                "items": [
                    {
                        "platform": "TikTok",
                        "content_type": "short_video",
                        "pillar": "product_education",
                        "angle": "ทดสอบคำกล่าวอ้างเสี่ยง",
                        "hook": "ทดสอบ",
                        "body": "SoClean ทิชชู่ ไร้ฝุ่น 100%",
                        "caption": "ไร้ฝุ่น 100%",
                        "cta": "สอบถามได้เลย",
                        "hashtags": ["#SoClean"],
                    }
                ]
            }
        if agent_name == "reviewer":
            return {
                "status": "ready_to_approve",
                "score": 100,
                "issues": [],
                "revision_notes": "",
            }
        return super()._mock_response(agent_name, variables)


def test_graph_runs_end_to_end() -> None:
    result = run_content_factory_graph(
        initial_state("campaign-test", llm_service=DeterministicMockLLMService())
    )

    assert result["review_passed"] is True
    assert result["retry_count"] == 0
    assert [item["channel"] for item in result["generated_content"]] == ["TikTok", "Facebook", "LINE"]
    assert len(result["visual_briefs"]) == 3


def test_failed_review_triggers_rewrite() -> None:
    request = schemas.GenerateContentRequest(force_initial_review_failure=True)
    result = run_content_factory_graph(
        initial_state("campaign-test", request, llm_service=DeterministicMockLLMService())
    )

    assert result["review_passed"] is True
    assert result["retry_count"] == 1
    bodies = " ".join(item["body"] for item in result["generated_content"])
    assert all(claim not in bodies for claim in FORBIDDEN_CLAIMS)
    assert "ปรับข้อความ" in bodies


def test_retry_stops_after_max_retry_count() -> None:
    request = schemas.GenerateContentRequest(force_initial_review_failure=True, max_retries=2)
    result = run_content_factory_graph(
        initial_state(
            "campaign-test",
            request,
            force_always_fail=True,
            llm_service=DeterministicMockLLMService(),
        )
    )

    assert result["review_passed"] is False
    assert result["retry_count"] == 2
    assert "Forced deterministic review failure" in result["review_feedback"]


def test_reviewer_cannot_pass_risky_claims() -> None:
    request = schemas.GenerateContentRequest(platforms=["TikTok"], max_retries=0)
    result = run_content_factory_graph(
        initial_state("campaign-test", request, llm_service=RiskyPassingReviewMockLLMService())
    )

    assert result["review_passed"] is False
    assert result["review_result"]["status"] == "revision_required"
    assert "พบคำกล่าวอ้างต้องห้าม 'ไร้ฝุ่น 100%'" in result["review_feedback"]
