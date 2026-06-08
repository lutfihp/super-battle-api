"""
Seed script: fetch DC Comics + Marvel Comics characters from SuperHero API CDN
and enrich with Comic Vine descriptions, then upsert into Supabase.

Usage:
    python seed.py           # upsert (safe to re-run)
    python seed.py --reset   # wipe all rows, then seed fresh
"""

import argparse
import re
import sys
import time

import requests
from supabase import create_client

from app.config import get_settings

SUPERHERO_CDN = "https://akabab.github.io/superhero-api/api/all.json"
COMICVINE_SEARCH = "https://comicvine.gamespot.com/api/search/"
PUBLISHERS = {"DC Comics", "Marvel Comics"}
STAT_FIELDS = ["intelligence", "strength", "speed", "durability", "power", "combat"]


def strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html or "").strip()


def fetch_superhero_characters() -> list[dict]:
    print("Fetching from SuperHero API CDN...")
    resp = requests.get(SUPERHERO_CDN, timeout=30)
    resp.raise_for_status()
    all_chars = resp.json()

    valid = []
    for c in all_chars:
        publisher = (c.get("biography") or {}).get("publisher", "")
        if publisher not in PUBLISHERS:
            continue
        stats = c.get("powerstats") or {}
        if not all(stats.get(f) for f in STAT_FIELDS):
            continue
        valid.append(c)

    print(f"  → {len(valid)} characters with complete stats from DC Comics + Marvel Comics")
    return valid


def fetch_comic_vine_description(name: str, api_key: str) -> str | None:
    params = {
        "query": name,
        "resources": "character",
        "api_key": api_key,
        "format": "json",
        "field_list": "id,name,description",
    }
    headers = {"User-Agent": "SuperBattle/1.0"}
    try:
        resp = requests.get(COMICVINE_SEARCH, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if not results:
            return None
        text = strip_html(results[0].get("description") or "")
        return text[:500] if text else None
    except Exception:
        return None


def fetch_existing_ids(db) -> set[int]:
    result = db.table("characters").select("id").execute()
    return {row["id"] for row in (result.data or [])}


def reset_all(db) -> None:
    print("Resetting all rows via truncate_all RPC...")
    try:
        db.rpc("truncate_all").execute()
        print("  → Done.")
    except Exception as e:
        print(f"  ! Reset failed: {e}")
        print("  Hint: run migration.sql in Supabase SQL editor first.")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed SuperBattle database")
    parser.add_argument("--reset", action="store_true", help="Wipe all rows before seeding")
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max Comic Vine API calls per run (use 190 to stay under the 200/hour cap). Default: no limit.",
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_anon_key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        sys.exit(1)

    db = create_client(settings.supabase_url, settings.supabase_anon_key)

    if args.reset:
        reset_all(db)

    chars = fetch_superhero_characters()
    total = len(chars)

    existing_ids = fetch_existing_ids(db)
    print(f"  → {len(existing_ids)} already in DB, will skip them")

    cv_enabled = bool(settings.comicvine_api_key)
    print(f"Seeding up to {total} characters (Comic Vine: {'on' if cv_enabled else 'off'}, limit: {args.limit or 'none'})...")

    cv_calls = 0
    seeded = 0
    skipped_existing = 0
    skipped_no_cv = 0

    for i, c in enumerate(chars, 1):
        char_id = int(c["id"])
        name = c["name"]

        if char_id in existing_ids:
            skipped_existing += 1
            print(f"  [{i}/{total}] {name} — already in DB, skipping")
            continue

        if args.limit and cv_calls >= args.limit:
            print(f"\nReached Comic Vine limit ({args.limit}). Run again in 1 hour to continue.")
            break

        description = None
        if cv_enabled:
            description = fetch_comic_vine_description(name, settings.comicvine_api_key)
            cv_calls += 1
            time.sleep(1.0)

        if not description:
            skipped_no_cv += 1
            print(f"  [{i}/{total}] {name} — no Comic Vine description, skipping")
            continue

        stats = c["powerstats"]
        bio = c.get("biography") or {}
        images = c.get("images") or {}

        row = {
            "id": char_id,
            "name": name,
            "publisher": bio.get("publisher"),
            "alignment": bio.get("alignment"),
            "intelligence": int(stats["intelligence"]),
            "strength": int(stats["strength"]),
            "speed": int(stats["speed"]),
            "durability": int(stats["durability"]),
            "power": int(stats["power"]),
            "combat": int(stats["combat"]),
            "image_url": images.get("sm"),
            "description": description,
        }

        db.table("characters").upsert(row, on_conflict="id").execute()
        seeded += 1
        print(f"  [{i}/{total}] {name} — OK")

    print(f"\nDone. {seeded} seeded, {skipped_existing} skipped (already in DB), {skipped_no_cv} skipped (no Comic Vine description).")


if __name__ == "__main__":
    main()
