# super-battle-api

FastAPI backend for SuperBattle — comic book character battle story generator. **Integration complete**: all endpoints talk to real Supabase (character data + battle cache) and real Fireworks AI (story narration via `gpt-oss-120b`).

## Status: Integration complete — seed complete — RLS enabled — deployed

All 5 endpoints wired to real services. 53 pytest tests pass. Supabase DB has **386 characters** seeded (DC Comics + Marvel Comics, both enriched with Comic Vine descriptions). Seeding is done.

## Run locally

```powershell
# From d:\Codading Repo\super-battle\super-battle-api
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs
```

Tests:
```powershell
venv\Scripts\activate
pytest
```

## Seed the database

```powershell
venv\Scripts\activate

# Resume / re-run safely (skips already-seeded characters)
python seed.py --limit 190

# Wipe everything and start fresh
python seed.py --reset --limit 190
```

- Characters **without** a Comic Vine description are skipped entirely (not stored in DB)
- `--limit 190` stays under Comic Vine's 200 req/hour cap
- **Current state: 386 characters in DB — seeding complete**

## Tech stack

- Python 3.11, FastAPI, Pydantic v2, pydantic-settings
- supabase>=2.10.0, openai>=1.50.0 (Fireworks OpenAI-compatible endpoint), requests>=2.32.0
- httpx2 (not httpx) — required by Starlette TestClient
- pytest + pytest-mock + FastAPI TestClient for all tests
- venv at `venv/` — always activate before running

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/api/health` | `{"status": "ok"}` |
| GET | `/api/characters/popular` | Top 20 by combined stats from Supabase |
| GET | `/api/characters/search?q=` | Name search (ILIKE) from Supabase |
| POST | `/api/battle` | 8-sentence Fireworks story, winner, scores, teams, cached flag |
| GET | `/api/stats` | Real COUNT(*) from Supabase battles + characters tables |

## File structure

```
app/
  config.py              # pydantic-settings; reads .env
  main.py                # FastAPI app factory, CORS, router registration
  models.py              # Character (+ description field), BattleRequest, BattleResponse (+ cached field), HealthResponse, StatsResponse
  routers/
    health.py
    characters.py        # calls get_popular_characters() / search_characters()
    battle.py            # calls get_characters_by_ids() + run_battle()
    stats.py             # real Supabase COUNT queries; returns 0,0 if no client
  services/
    supabase.py          # module-level singleton; returns None if no credentials
    characters.py        # rows_to_characters(), get_popular_characters(), search_characters(), get_characters_by_ids()
    battle.py            # TEAM_MULTIPLIERS, compute_score(), make_matchup_key(), run_battle() — cache check + Groq + cache write
    fireworks_service.py # generate_battle_story(team_a, team_b) → list[str] via Fireworks gpt-oss-120b (OpenAI SDK, base_url=https://api.fireworks.ai/inference/v1)
migration.sql            # Run once in Supabase SQL editor — creates characters, battles tables + truncate_all()
seed.py                  # Fetch SuperHero CDN → Comic Vine enrich → Supabase upsert; --reset, --limit flags
conftest.py              # autouse mock_services fixture patches all routers; client fixture
tests/                   # 53 tests across 11 files
```

## Key implementation details

- `conftest.py` is at **repo root** (not `tests/`) — puts `super-battle-api/` on sys.path
- `conftest.py` has an **autouse** `mock_services` fixture that patches all router-level service imports, keeping all 50 tests isolated from real Supabase/Fireworks calls
- `rows_to_characters()` maps DB `description` → both `Character.description` and `Character.powers_text` (for backward compat)
- `compute_score()` applies `TEAM_MULTIPLIERS = {1: 1.0, 2: 0.6, 3: 0.5}` — raw stat sum × multiplier, rounded to int. Winner is determined from multiplied scores.
- `run_battle()` checks the `battles` table cache first by `matchup_key`; only calls Fireworks on cache miss
- `make_matchup_key()` sorts both team ID lists so the same matchup always produces the same key regardless of team order
- Supabase `id` column is `INTEGER`; `Character.id` is `str` — `get_characters_by_ids()` converts `[int(i) for i in ids]` before the `.in_()` query
- Battle router returns HTTP 404 if any requested character ID is not found in DB
- LLM: `accounts/fireworks/models/gpt-oss-120b` on Fireworks serverless (~$0.15 in / $0.60 out per 1M tokens), max_tokens=600, temperature=0.8; pads to 8 sentences if response is short
- Comic Vine: 200 req/hour limit; seed uses 1s delay + `--limit` flag; strips HTML from description; truncates to 500 chars

## Environment variables (.env)

```
SUPERHERO_API_KEY=       # not used at runtime — seed.py uses CDN (no key needed)
COMICVINE_API_KEY=       # seed.py only
FIREWORKS_API_KEY=       # required at runtime for battle narration (Fireworks AI serverless)
SUPABASE_URL=            # required at runtime
SUPABASE_ANON_KEY=       # publishable key — used as fallback if SERVICE_KEY not set
SUPABASE_SERVICE_KEY=    # required at runtime — service_role key (bypasses RLS); find in Supabase → Project Settings → API
FRONTEND_URL=http://localhost:3000
```

## Database schema (Supabase)

**characters** — `id INTEGER PK, name, publisher, alignment, intelligence, strength, speed, durability, power, combat, image_url, description, updated_at`

**battles** — `matchup_key TEXT PK, story JSONB, winner, score_a, score_b, created_at`

**truncate_all()** — RPC function; called by `seed.py --reset` to wipe all rows without dropping schema

## Security — RLS (enabled 2026-06-10)

Both tables have Row-Level Security enabled. Applied via Supabase SQL editor:
- `ALTER TABLE characters ENABLE ROW LEVEL SECURITY;`
- `ALTER TABLE battles ENABLE ROW LEVEL SECURITY;`
- Anon `SELECT` policy on both tables (data is public, reads still work with anon key)
- No anon INSERT/UPDATE/DELETE — blocked
- Backend uses `SUPABASE_SERVICE_KEY` (service_role key) so writes (battle cache inserts, seeding) bypass RLS and continue to work

`supabase.py` prefers `SUPABASE_SERVICE_KEY`; falls back to `SUPABASE_ANON_KEY` if not set.

## What's next

1. **Smoke test production** — `curl https://superbattle-api.codading.site/api/characters/popular` and run a POST /api/battle to confirm writes still work
2. **Visual QA** — full battle flow on production via the frontend

## Cache migration note

The `battles` table was cleared (2026-06-08) when team-size multipliers were introduced. Any future change to `compute_score()` logic should also clear the `battles` table — use `DELETE FROM battles;` in Supabase SQL editor (NOT `truncate_all()`, which also wipes characters).
