-- Run once in the Supabase SQL editor.
-- Safe to re-run (IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS characters (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    publisher    TEXT,
    alignment    TEXT,
    intelligence INTEGER,
    strength     INTEGER,
    speed        INTEGER,
    durability   INTEGER,
    power        INTEGER,
    combat       INTEGER,
    image_url    TEXT,
    description  TEXT,
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS battles (
    matchup_key  TEXT PRIMARY KEY,
    story        JSONB NOT NULL,
    winner       TEXT NOT NULL,
    score_a      INTEGER NOT NULL,
    score_b      INTEGER NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Used by seed.py --reset to wipe data without dropping schema.
CREATE OR REPLACE FUNCTION truncate_all() RETURNS void
LANGUAGE plpgsql AS $$
BEGIN
  TRUNCATE characters, battles CASCADE;
END;
$$;

-- Enable RLS — blocks all direct public writes via the anon key.
ALTER TABLE characters ENABLE ROW LEVEL SECURITY;
ALTER TABLE battles    ENABLE ROW LEVEL SECURITY;

-- Allow public reads (data is not sensitive; blocks INSERT/UPDATE/DELETE via anon).
CREATE POLICY "anon_select_characters" ON characters
  FOR SELECT TO anon USING (true);

CREATE POLICY "anon_select_battles" ON battles
  FOR SELECT TO anon USING (true);
