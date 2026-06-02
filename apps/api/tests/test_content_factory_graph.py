from app.agents.content_factory import FORBIDDEN_CLAIMS, initial_state, run_content_factory_graph
from app import schemas


def test_graph_runs_end_to_end() -> None:
    result = run_content_factory_graph(initial_state("campaign-test"))

    assert result["review_passed"] is True
    assert result["retry_count"] == 0
    assert [item["channel"] for item in result["generated_content"]] == ["TikTok", "Facebook", "LINE"]
    assert len(result["visual_briefs"]) == 3


def test_failed_review_triggers_rewrite() -> None:
    request = schemas.GenerateContentRequest(force_initial_review_failure=True)
    result = run_content_factory_graph(initial_state("campaign-test", request))

    assert result["review_passed"] is True
    assert result["retry_count"] == 1
    bodies = " ".join(item["body"] for item in result["generated_content"])
    assert all(claim not in bodies for claim in FORBIDDEN_CLAIMS)
    assert "ปรับข้อความ" in bodies


def test_retry_stops_after_max_retry_count() -> None:
    request = schemas.GenerateContentRequest(force_initial_review_failure=True, max_retries=2)
    result = run_content_factory_graph(initial_state("campaign-test", request, force_always_fail=True))

    assert result["review_passed"] is False
    assert result["retry_count"] == 2
    assert "Forced deterministic review failure" in result["review_feedback"]
