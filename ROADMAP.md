# AdGen — Roadmap (Post-Phase-1)

Nothing here gets built until `PROJECT_SPEC.md`'s "Definition of done for
Phase 1" is actually met — one client running the full pipeline end to end,
a second client onboarded via config only, human approval working through
Telegram, one real video produced. Don't let any of this influence Phase 1
architecture beyond what's already accounted for (e.g. the `cost_logs`
table existing empty).

## Phase 2 — Workflow hardening

- More agents, only where a Phase 1 stage genuinely proved overloaded (e.g.
  split Research Agent into Research + Strategy if extraction quality or
  latency demands it)
- Retry/error handling hardening across the LangGraph pipeline
- Better Telegram UX (richer status, inline approve/reject buttons)

## Phase 3 — Productization

- Web dashboard (once Telegram-only genuinely feels limiting to a real
  client, not before)
- Auth / multi-user, so clients can self-serve instead of you running
  everything for them
- Billing (Stripe) — only once there's someone to actually charge
- Team management for multi-person client accounts
- Public/partner API

## Future capabilities (no timeline — capture the idea, don't build yet)

- **Competitor Intelligence:** auto-discover new competitors per client
  instead of relying on a static config list
- **Campaign Analytics:** ingest CTR, watch time, conversion rate,
  engagement per published ad
- **AI Feedback Loop:** generated ad → published → performance data →
  learning → better future ads. Depends entirely on Campaign Analytics
  existing first.
- **Multi-Platform Publishing:** generate platform-optimized variants for
  Facebook, Instagram, TikTok, YouTube Shorts, LinkedIn, X. Each platform
  has its own ad API/OAuth/review process — treat as N separate
  integrations, not one generic "publish" button.
- **Asset Library & Stock Footage:** per-client reusable logos, brand colors, fonts, music, product screenshots, and stock video footage (Pexels API or similar) — agents pull from this automatically instead of relying solely on kinetic typography / generic visuals.
- **Cost Tracking (logic, not just the table):** per-run LLM/video/scraping
  cost attribution, feeding into future billing

## Why this file exists separately from PROJECT_SPEC.md

Keeping the ambitious stuff written down but out of the active build spec
prevents two failure modes: forgetting good ideas, and prematurely
over-engineering Phase 1 to "leave room" for features that don't exist yet.
Revisit this file once Phase 1's definition of done is met — not before.
