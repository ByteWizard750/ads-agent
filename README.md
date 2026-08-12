# AdGen — Multi-Tenant AI Marketing Automation Platform (Phase 1)

AdGen is a configuration-driven, multi-tenant AI marketing automation engine. It researches competitor ads, extracts copy-grounded marketing angles, generates targeted ad scripts, and renders programmatic video ads — driven entirely by client YAML configuration without niche-specific code.

---

## Architecture & Pipeline Lifecycle

The core engine is orchestrated via **LangGraph** (Python) with built-in state checkpointing and a human-in-the-loop approval gate.

```
Todo ➔ Researching ➔ Analyzing ➔ Writing Script ➔ Awaiting Approval (Human Gate) ➔ Rendering Video ➔ Completed
```

### 1. Research Agent
- Scrapes competitor Meta/Facebook Ads Library data via Apify.
- Ranks ads using **ad longevity** ($\text{endDate} - \text{startDate}$) as the primary performance proxy and `pageLikeCount` as a secondary tiebreaker.
- Persists raw ad creative metadata into Supabase `ads` table.
- Extracts winning marketing angles, pain points, and hook styles grounded strictly in competitor copy into Supabase `concepts` table.

### 2. Script Agent
- Parses domain proprietary data from `clients/<client_id>/data/` (format-tolerant parser for CSV, JSON, Markdown, and TXT).
- Routes prompts via **OpenRouter** to frontier LLM models.
- Generates 3 distinct 30–60 second script variants:
  - **Variant A (`variant_a_pain_point`):** Leads with identified customer pain point.
  - **Variant B (`variant_b_stat`):** Leads with verified proprietary data stat (strictly blocked if data files are missing to prevent hallucinated stats).
  - **Variant C (`variant_c_solution`):** Leads with product solution.
- Persists generated scripts into Supabase `scripts` table and pauses execution at the `Awaiting Approval` Kanban gate.

### 3. Video Agent
- Programmatically renders approved scripts into 30–60 second vertical (9:16) videos using Remotion CLI and React.
- **Audio/TTS:** Uses **ElevenLabs API** (`eleven_multilingual_v2`) for natural, SSML-paused voiceovers, falling back to Edge-TTS.
- **Visuals:** Composites real free stock footage via the **Pexels API** behind custom kinetic typography and terminal-styled data overlay cards.
- **Syncing:** Achieves exact audio-visual syncing by matching visual scene lengths precisely to WebVTT chunk boundaries of the generated voiceover.
- Uploads final rendered `.mp4` video assets directly to **Supabase Storage** and persists public URLs to the DB.

---

## Tech Stack

- **Orchestration:** LangGraph (Python)
- **Database & Storage:** PostgreSQL + Object Storage via Supabase (8 client-scoped tables)
- **Backend Framework:** FastAPI & Uvicorn
- **LLM Access:** OpenRouter (`google/gemini-2.5-pro` for direct script writing and research)
- **Scraping:** Apify (`apify/facebook-ads-scraper`)
- **Video Generation:** Remotion (React/TypeScript), Node.js, `ffmpeg`
- **Audio TTS:** ElevenLabs API + Edge-TTS
- **Stock Media:** Pexels API
- **Scheduler:** APScheduler

---

## Data Model (Supabase PostgreSQL)

Every table is multi-tenant scoped by `client_id`:
- `clients` — Client registrations & config paths
- `runs` — Pipeline execution run logs
- `ads` — Raw and formatted competitor ad data
- `concepts` — Extracted marketing angles & pain points
- `scripts` — Script variants (A/B/C) and approval status
- `videos` — Rendered video metadata & storage links
- `kanban_state` — Enforced enum lifecycle state tracking
- `cost_logs` — Execution cost logging table

---

## Repository Structure

```
ads-agent/
├── clients/
│   └── crowdwisdom/
│       ├── config.yaml          # Reference client configuration
│       ├── assets/               # Brand logos, fonts, media
│       └── data/                 # Proprietary stats (CSV/JSON/MD/TXT)
├── data/
│   └── ads_sample_raw_full.json  # Raw dataset cache (862 ads)
├── remotion/                     # Video Generation Engine (React/TS)
│   ├── src/                      # Remotion composition layers & scenes
│   ├── public/                   # Downloaded audio & stock footage
│   └── package.json
├── scripts/
│   ├── apply_migration.py       # SQL migration execution script
│   ├── explore_apify_actors.py   # Apify actor search & test script
│   ├── run_research_agent.py     # Standalone Research Agent runner
│   ├── run_script_agent.py       # Research + Script Agent runner
│   ├── test_video_agent.py       # Video generation integration test
│   ├── render_scene_preview.py   # Quick local scene preview renderer
│   ├── check_cached_ads.py       # Local JSON cache URL inspector
│   └── verify_db.py              # Supabase table verification query
├── src/
│   ├── config.py                 # Pydantic configuration loader
│   ├── agents/
│   │   ├── research.py           # Research Agent implementation
│   │   ├── script.py             # Script Agent implementation
│   │   └── video.py              # Video Rendering Agent implementation
│   ├── db/
│   │   └── supabase.py           # Supabase REST client & helpers
│   ├── pipeline/
│   │   ├── state.py              # Pipeline state definition
│   │   └── graph.py              # LangGraph 3-node stateful graph
│   └── utils/
│       ├── data_parser.py        # Proprietary data parser
│       └── pexels.py             # Pexels API stock video downloader
├── supabase/
│   └── migrations/
│       └── 20260731000000_init_schema.sql  # Migration script
├── .env.example
├── .gitignore
├── requirements.txt
├── PROJECT_SPEC (2).md           # Active Phase 1 specification
└── ROADMAP.md                    # Post-Phase-1 scope & roadmap
```

---

## Getting Started

### 1. Environment Setup

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/ByteWizard750/ads-agent.git
cd ads-agent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-secret-key
OPENROUTER_API_KEY=your-openrouter-api-key
APIFY_API_TOKEN=your-apify-token
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### 3. Database Migration & Verification

Execute the migration file `supabase/migrations/20260731000000_init_schema.sql` in your Supabase SQL Editor, then verify table creation:

```bash
python scripts/verify_db.py
```

### 4. Run the Pipeline

Run the Research & Script agents end-to-end through the LangGraph pipeline:

```bash
python scripts/run_script_agent.py
```

---

## License

MIT License.
