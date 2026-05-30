-- Run this in your Supabase SQL editor to create the required tables.
-- Dashboard → SQL Editor → New Query → paste this → Run

CREATE TABLE IF NOT EXISTS team_profiles (
    user_id     TEXT PRIMARY KEY,
    username    TEXT,
    skills      TEXT,
    interests   TEXT,
    timezone    TEXT,
    experience  TEXT,
    looking_for TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS winners (
    hackathon  TEXT PRIMARY KEY,
    team       TEXT,
    project    TEXT,
    prize      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
