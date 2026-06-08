"""
Backup and restore Supabase characters table to/from a local JSON file.

Usage:
    python backup_db.py              # backup characters to backup_characters.json
    python backup_db.py --restore    # restore from backup_characters.json
    python backup_db.py --file my_backup.json   # custom file path
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from supabase import create_client

from app.config import get_settings

DEFAULT_FILE = "backup_characters.json"
PAGE_SIZE = 1000


def get_db():
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_anon_key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        sys.exit(1)
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def backup(file_path: str) -> None:
    db = get_db()
    print("Fetching all characters from Supabase...")

    rows = []
    offset = 0
    while True:
        result = (
            db.table("characters")
            .select("*")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = result.data or []
        rows.extend(batch)
        print(f"  → fetched {len(rows)} so far...")
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    payload = {
        "backed_up_at": datetime.utcnow().isoformat() + "Z",
        "count": len(rows),
        "characters": rows,
    }

    Path(file_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. {len(rows)} characters saved to {file_path}")


def restore(file_path: str) -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: {file_path} not found")
        sys.exit(1)

    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("characters", [])
    backed_up_at = payload.get("backed_up_at", "unknown")

    print(f"Restoring {len(rows)} characters (backed up at {backed_up_at})...")

    db = get_db()

    inserted = 0
    for i in range(0, len(rows), 100):
        batch = rows[i : i + 100]
        db.table("characters").upsert(batch, on_conflict="id").execute()
        inserted += len(batch)
        print(f"  → {inserted}/{len(rows)} upserted")

    print(f"\nDone. {inserted} characters restored from {file_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup/restore SuperBattle characters table")
    parser.add_argument("--restore", action="store_true", help="Restore from backup file instead of creating one")
    parser.add_argument("--file", default=DEFAULT_FILE, help=f"Backup file path (default: {DEFAULT_FILE})")
    args = parser.parse_args()

    if args.restore:
        restore(args.file)
    else:
        backup(args.file)


if __name__ == "__main__":
    main()
