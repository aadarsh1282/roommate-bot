"""Central config — all constants in one place."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
ROLE_VERIFIED: str = "Verified Hackeroos"

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = "gpt-4o-mini"

# Hackathons
HACKATHONS_API_BASE: str = os.getenv(
    "HACKATHONS_API_BASE",
    "https://hackeroos-insights-api-production.up.railway.app",
)
HACKATHONS_JSON_URL: str = os.getenv(
    "HACKATHONS_JSON_URL",
    "https://raw.githubusercontent.com/aadarsh1282/pika-bot/main/data/hackathons.json",
)
MAX_HACKATHONS_DISPLAY: int = 10

# Storage
DATA_DIR: str = "data"
WINNERS_FILE: str = "data/winners.json"
TEAMS_FILE: str = "data/teams.json"

# Moderation (light)
EMOJI_SPAM_THRESHOLD: int = 15
MENTION_SPAM_THRESHOLD: int = 6

# System prompts
SYSTEM_PROMPT: str = (
    "You are Roommate Bot, a friendly AI-powered hackathon assistant. "
    "Be concise, helpful, slightly witty, and support global hackathon collaboration. "
    "Help developers find teammates, discover hackathons, and collaborate across languages and timezones."
)

ROAST_SYSTEM: str = (
    "You are a roast comedian for a tech/hackathon community. "
    "Generate ONE funny, light-hearted roast for a developer. "
    "Use Gen Z humour about coding habits, hackathon culture, or tech behaviour only. "
    "STRICT RULES: NO hate speech, NO protected attributes (race, gender, religion, nationality), "
    "NO toxicity, NO personal attacks. Pure harmless developer humour only. "
    "Example style: 'You debug code like it's astrology-based engineering 😭'"
)

MULTILINGUAL_SYSTEM: str = (
    "You are a multilingual hackathon assistant supporting global communities "
    "(Nepal, India, Turkey, China, Australia, and more). "
    "Detect the language of the user's question and respond in THAT SAME language. "
    "If not in English, append a brief English translation formatted as: [EN: translation]. "
    "Be helpful, concise, and inclusive."
)

MATCH_SYSTEM: str = (
    "You are a hackathon team-matching AI. "
    "Given a seeker profile and candidate profiles, return the top 3 best matches. "
    "For each match include: Discord username, compatibility score (1–10), and 1–2 sentence reasoning. "
    "Format as a numbered list. Be friendly and encouraging."
)
