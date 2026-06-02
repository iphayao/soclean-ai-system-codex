# Agent Workflows

## Content Factory

The content factory is implemented in `apps/api/app/agents/content_factory.py` with LangGraph.

Workflow:

```text
START
-> load_brand_memory
-> generate_customer_insights
-> generate_content_strategy
-> generate_campaign_plan
-> generate_content
-> generate_visual_briefs
-> review_content
-> rewrite_content when review fails and retry_count < max_retries
-> save_content
-> END
```

## State

`ContentFactoryState` carries:

- campaign and brand context
- language and platforms
- SoClean product facts
- safe and forbidden claims
- generated plan, copy, visual briefs, and review result
- retry count and saved content IDs
- database session and LLM service instance

## LLM Service

The LLM service loads prompt files from `prompts` by agent name:

- `campaign_planner`
- `copywriter`
- `visual_brief`
- `reviewer`

When `OPENAI_API_KEY` is not configured, deterministic mock JSON is returned. This keeps tests repeatable and lets the full workflow run locally without external services.

When live LLM mode is enabled, the service logs available usage metadata to `llm_usage_logs`, including model name, prompt tokens, completion tokens, and total tokens.

## Reviewer Rule Engine

The deterministic reviewer rule engine lives in `apps/api/app/rules/claim_rules.py`.

It runs before LLM review approval is accepted. Risky claims cannot pass automatically even if the LLM reviewer returns a passing status.

Banned claims:

- `ไร้ฝุ่น 100%`
- `ไม่ก่อภูมิแพ้`
- `ฆ่าเชื้อโรค`
- `ปลอดภัยที่สุด`
- `medical grade`
- `antibacterial`
- `hypoallergenic`

Preferred safer language:

- `ไร้ฝุ่น 100%` -> `ฝุ่นน้อย` or `ไม่ฟุ้งง่าย`
- `ไม่ก่อภูมิแพ้` -> `เหมาะสำหรับใช้ในชีวิตประจำวัน`
- `ฆ่าเชื้อโรค` -> remove the claim
- `ปลอดภัยที่สุด` -> `สะอาด น่าใช้`
- `medical grade` -> remove the claim

Scoring starts at 100 and deducts for banned claims, unsupported absolutes, missing CTA, missing product facts, and weak Thai placeholder copy.

## Content Statuses

Generated content that passes automated review is saved as `in_review`, not `approved`. A human must approve it in the dashboard before export.

Export requires both approved content status and an approved approval record.
