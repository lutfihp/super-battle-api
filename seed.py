"""
One-time seed script: fetches DC characters from SuperHero API CDN and
Comic Vine, then upserts into Supabase.

Stub mode — no network calls made. Real implementation goes here in the
integration phase.

Run with:
    python seed.py
"""


def main() -> None:
    print("SuperBattle seed script — stub mode (no network calls).")
    print()
    print("Steps this script will execute in the integration phase:")
    print("  1. Fetch all.json from SuperHero API CDN (no key required)")
    print("  2. Filter: biography.publisher == 'DC Comics'")
    print("  3. For ~60 popular characters, fetch powers from Comic Vine search API")
    print("  4. Upsert all rows into Supabase 'characters' table")
    print()
    print("Requires env vars: SUPERHERO_API_KEY, COMICVINE_API_KEY,")
    print("  SUPABASE_URL, SUPABASE_ANON_KEY")


if __name__ == "__main__":
    main()
