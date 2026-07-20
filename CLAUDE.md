# super-battle-api

FastAPI backend for SuperBattle — comic book character battle story generator. **Integration complete**: all endpoints talk to real Supabase (character data + battle cache) and real Fireworks AI (story narration via `gpt-oss-120b`).

## Status: Integration complete — seed complete — RLS enabled — deployed

All 5 endpoints wired to real services. 55 pytest tests pass. Supabase DB has **386 characters** seeded (DC Comics + Marvel Comics, both enriched with Comic Vine descriptions). Seeding is done.

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
    battle.py            # TEAM_MULTIPLIERS, compute_score(), make_matchup_key(), run_battle() — cache check + Fireworks + cache write
    fireworks_service.py # generate_battle_story(team_a, team_b) → list[str] via Fireworks gpt-oss-120b (OpenAI SDK, base_url=https://api.fireworks.ai/inference/v1)
migration.sql            # Run once in Supabase SQL editor — creates characters, battles tables + truncate_all()
seed.py                  # Fetch SuperHero CDN → Comic Vine enrich → Supabase upsert; --reset, --limit flags
conftest.py              # autouse mock_services fixture patches all routers; client fixture
tests/                   # 55 tests across 11 files
```

## Key implementation details

- `conftest.py` is at **repo root** (not `tests/`) — puts `super-battle-api/` on sys.path
- `conftest.py` has an **autouse** `mock_services` fixture that patches all router-level service imports, keeping all 55 tests isolated from real Supabase/Fireworks calls
- `rows_to_characters()` maps DB `description` → both `Character.description` and `Character.powers_text` (for backward compat)
- `compute_score()` applies `TEAM_MULTIPLIERS = {1: 1.0, 2: 0.6, 3: 0.5}` — raw stat sum × multiplier, rounded to int. Winner is determined from multiplied scores.
- `run_battle()` **computes `winner` first**, then calls `generate_battle_story(team_a, team_b, winner)` — the LLM must know who wins before it writes, otherwise sentence 8 contradicts the score.
- `run_battle()` checks the `battles` table cache first by `matchup_key`; only calls Fireworks on cache miss
- `make_matchup_key()` sorts both team ID lists so the same matchup always produces the same key regardless of team order
- Supabase `id` column is `INTEGER`; `Character.id` is `str` — `get_characters_by_ids()` converts `[int(i) for i in ids]` before the `.in_()` query
- Battle router returns HTTP 404 if any requested character ID is not found in DB
- **LLM call** (`app/services/fireworks_service.py`):
  - Model: `accounts/fireworks/models/gpt-oss-120b` on Fireworks serverless (~$0.15 in / $0.60 out per 1M tokens)
  - `max_tokens=1500`, `temperature=0.8`, **`extra_body={"reasoning_effort": "low"}`** — DO NOT REMOVE. gpt-oss uses OpenAI's Harmony format; with default reasoning it burns the entire token budget on hidden reasoning and returns `content=None` with `finish_reason=length`.
  - Prompt enforces 8-sentence structure: 1-2 setup, 3-6 escalation, **7 = decisive winning strike**, **8 = aftermath naming the victors**. Winner name is baked into sentences 7 and 8 of the prompt.
  - Parser sentence-splits on `.!?` boundaries (not just newlines) because gpt-oss frequently returns all 8 sentences as one paragraph. Pads with filler if fewer than 8 sentences parsed.
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

Nothing blocking. Fireworks swap is deployed, VPS env is updated, cache is cleared, live battles work end-to-end with winner-aligned narratives. Frontend `/how-it-works` copy is in sync (commit `be1d1b0` in `super-battle-app`, 2026-07-20) — architecture diagram, prompt inspector, cache-miss latency, and stack card all reflect Fireworks / gpt-oss-120b.

Optional follow-ups:
1. **Visual QA** — spot-check a handful of matchups on `superbattle.codading.site` to make sure narratives read well across weight classes (David-vs-Goliath, 1v3, etc.). Confirm sentence 7 always aligns with the displayed winner.
2. **Prompt quality iteration** — if users report flat/repetitive prose, first try `kimi-k2p6` on Fireworks (~6× cost but noticeably better creative writing). Swap is one line in `fireworks_service.py:_MODEL`.
3. **Batch-inference option** — Fireworks bills batch at 50% of serverless. Not worth it for interactive requests but useful if we ever pre-warm the cache with popular matchups.

## Cache migration note

The `battles` table has been cleared four times:
- **2026-06-08** — team-size multipliers introduced
- **2026-07-20 (a)** — LLM swap Groq → Fireworks gpt-oss-120b (old prose was Groq-flavored)
- **2026-07-20 (b)** — first gpt-oss run had a parser bug that stored a real paragraph followed by 7 filler lines
- **2026-07-20 (c)** — old winner-agnostic prompts were still cached; re-cleared after the winner-aware prompt landed

Any future change to `compute_score()`, the LLM model, OR the prompt structure should also clear the `battles` table — use `DELETE FROM battles;` in Supabase SQL editor (NOT `truncate_all()`, which also wipes characters).

## LLM swap history (2026-07-20)

Switched narration provider from **Groq → Fireworks AI**:
- **Was:** `groq` SDK, model `llama-3.3-70b-versatile`, in `app/services/groq_service.py`
- **Now:** `openai` SDK with `base_url=https://api.fireworks.ai/inference/v1`, model `accounts/fireworks/models/gpt-oss-120b`, in `app/services/fireworks_service.py`
- **Why:** ~10× cheaper (~$0.15 in / $0.60 out per 1M tokens vs. other Fireworks options), prepaid Fireworks credit, comparable output quality for 8-sentence action narration
- **Env var renamed:** `GROQ_API_KEY` → `FIREWORKS_API_KEY` (updated on VPS)
- **Test isolation:** `tests/test_fireworks_service.py` patches `app.services.fireworks_service.OpenAI` (not `Groq`)

Three fix commits followed the initial swap, each addressing a distinct gpt-oss quirk:

| Commit | Fix | Symptom it addressed |
|---|---|---|
| `9f542ee` | Initial Groq → Fireworks swap | — |
| `ec59dcd` | Parser sentence-splits on `.!?`, not just `\n` | gpt-oss returned all 8 sentences as one paragraph → parser saw 1 "sentence" → padded with 7 filler lines |
| `546a2c0` | Compute winner first, pass into prompt; set `reasoning_effort=low`, `max_tokens=1500` | (a) narrative ended in stalemate/loser-wins prose while frontend showed the score-computed winner; (b) default reasoning burned all 600 output tokens on hidden reasoning → `content=None`, `finish_reason=length` |

**Gotchas to preserve** (any refactor of `fireworks_service.py` must keep these or things break):
- `extra_body={"reasoning_effort": "low"}` on the chat completion call
- `max_tokens >= 1500` (reasoning tokens count against it even at "low")
- Sentence-split regex `r"(?<=[.!?])\s+"` — do not go back to newline-only splitting
- Winner passed as positional/kwarg to `generate_battle_story()` — do not remove
