# AdGen — Project Spec (Phase 1: Core Engine)

## What this is

AdGen is a multi-tenant AI marketing automation platform that researches
competitor ads, extracts winning marketing angles, writes ad scripts, and
renders video ads — for any client, driven entirely by configuration, not code.

CrowdWisdomTrading is client #1 and the reference implementation that proves
the architecture. Nothing in the agent code should ever reference
CrowdWisdomTrading, trading, or fintech by name — that all lives in config.

**This document covers Phase 1 only: the core engine.** No dashboard, no
auth, no billing, no publishing, no analytics. Those are real future goals,
but they live in `ROADMAP.md`, not here — Phase 1 is done when the pipeline
below runs end to end for one client and produces one approved video.

## Pipeline (3 agents, per client, per run)

1. **Research Agent** (research + analysis in one agent for now)
   - Scrape top-performing Meta/Facebook Ads Library ads for the client's
     niche (search terms / competitor list from client config), last 30 days
   - Save raw ad data + creative metadata
   - Extract marketing angles, pain points, hook styles, and high-performing
     patterns from the scraped ads
   - *Split into separate Research and Strategy agents later, only if this
     stage genuinely gets overloaded — don't pre-split it.*

2. **Script Agent** (copywriting + hook engineering in one agent for now)
   - Generate 3 distinct 30-60 second script variants per run:
     - Variant A: leads with an identified pain point
     - Variant B: leads with a stat from the client's proprietary/unique data
     - Variant C: leads with how the client's product solves the problem
   - Each variant gets its own scroll-stopping hook (first 1-2 seconds)
   - Human approval gate before proceeding to video (kanban "awaiting
     approval" state, approvable via Telegram)

3. **Video Agent**
   - Render approved scripts into 30-60 second videos programmatically
   - TTS voiceover, B-roll/visual assembly, captions
   - Output saved to Supabase Storage

*No Publishing Agent in Phase 1 — actually posting to ad platforms requires
each platform's own API/OAuth/review process, which is a separate, slower
problem. That's Phase 3+, in `ROADMAP.md`.*

## Kanban states (per script/run)

```
Todo → Researching → Analyzing → Writing Script → Awaiting Approval
     → Rendering Video → Completed
```

Telegram is the control surface for Phase 1 — approve/reject scripts,
check status, per client. No web dashboard yet.

## Tech stack

- **Orchestration:** LangGraph (Python) — stateful graph, human-in-the-loop
  approval nodes, retries, persistent execution state
- **LLM access:** OpenRouter — per-agent model routing (cheap/free model for
  research+extraction, frontier paid model for script/hook generation)
- **Scraping:** Apify (Meta/Facebook Ads Library actor)
- **Video rendering:** Remotion (programmatic, CLI-renderable) + Edge-TTS to
  start (ElevenLabs/HeyGen/OpenMontage are optional future upgrades, not
  Phase 1 requirements)
- **Database:** PostgreSQL via Supabase — also provides file storage, needed
  for multi-tenancy from day one
- **Backend:** FastAPI, wrapping the LangGraph pipeline behind endpoints
- **Scheduling:** APScheduler (recurring per-client runs, e.g. every 30 days)
- **Control surface:** Telegram bot (multi-client commands: /status <client>,
  /approve <script_id>, /newclient)
- **Deploy:** Railway or Fly.io

## Data model (Supabase/Postgres)

Tables, every one scoped by `client_id`: `clients`, `runs`, `ads`,
`concepts`, `scripts`, `videos`, `kanban_state`, `cost_logs`.

(`cost_logs` exists as a table now so cost tracking is free to add later —
but don't build cost tracking *logic* in Phase 1, just leave the table.)

## Client config (drives every agent — nothing niche-specific in agent code)

```
clients/
    crowdwisdom/
        config.yaml   # brand name, niche, competitors, tone, data source refs
        assets/       # logos, brand colors, fonts (used later, not Phase 1)
        data/         # proprietary/unique data files
```

## First client: CrowdWisdomTrading

- Niche: trading/fintech education and signals
- Unique data source: 2 proprietary data files, ingested into
  `clients/crowdwisdom/data/`
- Proves the pipeline generalizes before client #2 is added (client #2 is a
  Phase 1 *validation step*, not a Phase 2 feature — add a second, even
  fake, client before considering Phase 1 done)

## Build order

1. Repo scaffold + Supabase schema (all 8 tables above)
2. LangGraph pipeline skeleton — 3 nodes wired end to end, no real logic
   yet, client config flowing through graph state
3. Research Agent — Apify integration, client-scoped config
4. Script Agent — OpenRouter, per-agent model routing, pulls client's unique
   data from Supabase storage, human approval node
5. Video Agent — Remotion + Edge-TTS, output to Supabase storage
6. Telegram bot — multi-client commands, wired to the approval node
7. Scheduler — APScheduler triggering the graph per client on interval
8. Kanban view — reads `kanban_state` live (simple web view is fine)
9. Add a second (test) client — validates config-only onboarding actually
   works before calling Phase 1 done

## Definition of done for Phase 1

- One client (CrowdWisdomTrading) runs the full pipeline end to end
- A second client can be onboarded by adding a config folder only — zero
  code changes
- A human can approve/reject a script via Telegram and see the kanban state
  change accordingly
- One real rendered video comes out the other end

## Explicitly out of scope for Phase 1

See `ROADMAP.md` for all of this — do not build any of it yet:
dashboard, auth/multi-user, billing, publishing to ad platforms, campaign
analytics, competitor auto-discovery, AI feedback loop, multi-platform
creative variants, asset library automation, cost-tracking logic (table
only, no logic).
