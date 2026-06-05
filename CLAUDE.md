# super-battle-api

FastAPI backend for SuperBattle — DC character battle story generator. Currently in **stub mode**: all endpoints return realistic hardcoded data. The integration phase wires in Supabase (character data) and Groq (AI story narration).

## Status: Stub complete, integration phase next

All 3 endpoints work and return realistic stub data. 30 pytest tests pass. Ready to wire real data sources.

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

## Tech stack

- Python 3.11, FastAPI, Pydantic v2, pydantic-settings
- httpx2 (not httpx) — required by Starlette TestClient
- pytest + FastAPI TestClient for all tests
- venv at `venv/` — always activate before running

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/api/health` | `{"status": "ok"}` |
| GET | `/api/characters/popular` | 4 stub DC characters |
| GET | `/api/characters/search?q=` | filtered stub results |
| POST | `/api/battle` | 8-sentence story, winner, scores, teams |

## File structure

```
app/
  config.py          # pydantic-settings; reads .env
  main.py            # FastAPI app factory, CORS, router registration
  models.py          # Character, BattleRequest, BattleResponse, HealthResponse
  routers/
    health.py
    characters.py
    battle.py
  services/
    characters.py    # STUB_CHARACTERS list (4 DC chars with real stat values)
    battle.py        # compute_score(), make_matchup_key(), run_battle_stub()
    supabase.py      # returns None until credentials set (stub guard)
conftest.py          # pytest fixture: TestClient at repo root (not tests/)
tests/               # 30 tests across 6 files
seed.py              # stub seed script (no-op until integration phase)
```

## Key implementation details

- `compute_score` uses `getattr()` on Pydantic models (not dict `.get()`)
- `conftest.py` is at the **repo root**, not inside `tests/` — this is what puts `super-battle-api/` on sys.path
- CORS `allow_origins` is read from `settings.frontend_url` (defaults to `http://localhost:3000`)
- `run_battle_stub()` always returns Team A wins: Batman(335) + Superman(579) = 914 vs Joker(221) + Wonder Woman(528) = 749
- Score = sum of all 6 stats (intelligence + strength + speed + durability + power + combat) per character

## Environment variables (.env)

```
SUPERHERO_API_KEY=
COMICVINE_API_KEY=
GROQ_API_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
FRONTEND_URL=http://localhost:3000
```

All optional in stub mode. Copy `.env.example` to `.env` to start.

## Integration phase (next steps)

1. **Supabase**: uncomment `create_client` in `services/supabase.py`, add `supabase>=2.10.0` to requirements.txt, run `seed.py` to populate `characters` table
2. **Characters endpoints**: replace `STUB_CHARACTERS` with Supabase queries in `routers/characters.py`
3. **Battle endpoint**: replace `run_battle_stub()` with real logic — query Supabase for characters by ID, call Groq for 8-sentence story, cache result in Supabase by `make_matchup_key()`
4. **Groq**: add story narration using `groq` SDK (already in `GROQ_API_KEY` setting)
5. **Docker**: test `docker build` on server — Dockerfile is written but not tested locally
