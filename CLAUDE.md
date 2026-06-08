# super-battle-api

FastAPI backend for SuperBattle — comic book character battle story generator. **Integration complete**: all endpoints talk to real Supabase (character data + battle cache) and real Groq (AI story narration).

## Status: Integration complete — seed in progress

All 5 endpoints wired to real services. 53 pytest tests pass. Supabase DB has ~121 characters seeded so far (DC + Marvel with Comic Vine descriptions). Seed needs 2 more runs (1 hour apart, 190 characters each) to finish.

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

# First run / resume (safe to re-run — skips already-seeded characters)
python seed.py --limit 190

# Wipe everything and start fresh
python seed.py --reset --limit 190
```

- Characters **without** a Comic Vine description are skipped entirely (not stored in DB)
- `--limit 190` stays under Comic Vine's 200 req/hour cap — run once per hour until "Done" prints
- Current state: ~121 characters in DB, ~302 remaining across 2 more runs

## Tech stack

- Python 3.11, FastAPI, Pydantic v2, pydantic-settings
- supabase>=2.10.0, groq>=0.9.0, requests>=2.32.0
- httpx2 (not httpx) — required by Starlette TestClient
- pytest + pytest-mock + FastAPI TestClient for all tests
- venv at `venv/` — always activate before running

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/api/health` | `{"status": "ok"}` |
| GET | `/api/characters/popular` | Top 20 by combined stats from Supabase |
| GET | `/api/characters/search?q=` | Name search (ILIKE) from Supabase |
| POST | `/api/battle` | 8-sentence Groq story, winner, scores, teams, cached flag |
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
    groq_service.py      # generate_battle_story(team_a, team_b) → list[str] via llama-3.3-70b-versatile
migration.sql            # Run once in Supabase SQL editor — creates characters, battles tables + truncate_all()
seed.py                  # Fetch SuperHero CDN → Comic Vine enrich → Supabase upsert; --reset, --limit flags
conftest.py              # autouse mock_services fixture patches all routers; client fixture
tests/                   # 53 tests across 11 files
```

## Key implementation details

- `conftest.py` is at **repo root** (not `tests/`) — puts `super-battle-api/` on sys.path
- `conftest.py` has an **autouse** `mock_services` fixture that patches all router-level service imports, keeping all 50 tests isolated from real Supabase/Groq calls
- `rows_to_characters()` maps DB `description` → both `Character.description` and `Character.powers_text` (for backward compat)
- `compute_score()` applies `TEAM_MULTIPLIERS = {1: 1.0, 2: 0.6, 3: 0.5}` — raw stat sum × multiplier, rounded to int. Winner is determined from multiplied scores.
- `run_battle()` checks the `battles` table cache first by `matchup_key`; only calls Groq on cache miss
- `make_matchup_key()` sorts both team ID lists so the same matchup always produces the same key regardless of team order
- Supabase `id` column is `INTEGER`; `Character.id` is `str` — `get_characters_by_ids()` converts `[int(i) for i in ids]` before the `.in_()` query
- Battle router returns HTTP 404 if any requested character ID is not found in DB
- Groq model: `llama-3.3-70b-versatile`, max_tokens=600, temperature=0.8; pads to 8 sentences if response is short
- Comic Vine: 200 req/hour limit; seed uses 1s delay + `--limit` flag; strips HTML from description; truncates to 500 chars

## Environment variables (.env)

```
SUPERHERO_API_KEY=       # not used at runtime — seed.py uses CDN (no key needed)
COMICVINE_API_KEY=       # seed.py only
GROQ_API_KEY=            # required at runtime for battle narration
SUPABASE_URL=            # required at runtime
SUPABASE_ANON_KEY=       # required at runtime (publishable key, not secret)
FRONTEND_URL=http://localhost:3000
```

## Database schema (Supabase)

**characters** — `id INTEGER PK, name, publisher, alignment, intelligence, strength, speed, durability, power, combat, image_url, description, updated_at`

**battles** — `matchup_key TEXT PK, story JSONB, winner, score_a, score_b, created_at`

**truncate_all()** — RPC function; called by `seed.py --reset` to wipe all rows without dropping schema

## What's next

1. **Finish seed** — run `python seed.py --limit 190` once per hour for 2 more runs (~302 characters remaining)
2. **Manual API validation** — start server, hit `/api/characters/popular`, run a real battle via POST, check `/api/stats` for live counts
3. **Frontend visual QA** — start both servers, test the full battle flow in browser
4. **Docker deploy** — Dockerfile exists but not yet tested; deploy to server

## Cache migration note

The `battles` table was cleared (2026-06-08) when team-size multipliers were introduced. Any future change to `compute_score()` logic should also clear the `battles` table — use `DELETE FROM battles;` in Supabase SQL editor (NOT `truncate_all()`, which also wipes characters).
