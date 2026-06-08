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

    cv_enabled = bool(settings.comicvine_api_key)
    print(f"Seeding {total} characters (Comic Vine enrichment: {'on' if cv_enabled else 'off'})...")

    for i, c in enumerate(chars, 1):
        name = c["name"]
        stats = c["powerstats"]
        bio = c.get("biography") or {}
        images = c.get("images") or {}

        description = None
        if cv_enabled:
            description = fetch_comic_vine_description(name, settings.comicvine_api_key)
            time.sleep(0.5)

        row = {
            "id": int(c["id"]),
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
        status = "OK" if description else "no Comic Vine result"
        print(f"  [{i}/{total}] {name} — {status}")

    print(f"\nDone. {total} characters seeded.")


if __name__ == "__main__":
    main()
