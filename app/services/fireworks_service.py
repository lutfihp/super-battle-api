import re

from openai import OpenAI
from app.config import get_settings
from app.models import Character

_FILLER = "The battle rages on with neither side yielding."
_MODEL = "accounts/fireworks/models/gpt-oss-120b"
_BASE_URL = "https://api.fireworks.ai/inference/v1"
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _format_team(team: list[Character]) -> str:
    lines = []
    for c in team:
        stats = (
            f"intelligence:{c.intelligence}, strength:{c.strength}, "
            f"speed:{c.speed}, durability:{c.durability}, "
            f"power:{c.power}, combat:{c.combat}"
        )
        context = (c.description or c.powers_text or "")[:300]
        lines.append(f"  - {c.name} ({stats})\n    Context: {context}")
    return "\n".join(lines)


def generate_battle_story(
    team_a: list[Character], team_b: list[Character]
) -> list[str]:
    settings = get_settings()
    client = OpenAI(api_key=settings.fireworks_api_key, base_url=_BASE_URL)

    prompt = f"""You are a battle narrator. Two teams of comic book heroes/villains are fighting.

Team A:
{_format_team(team_a)}

Team B:
{_format_team(team_b)}

Write exactly 8 sentences narrating the battle. Each sentence on its own line.
Return only the 8 sentences, nothing else."""

    response = client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.8,
    )

    text = response.choices[0].message.content.strip()
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip())
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(flat) if s.strip()]
    while len(sentences) < 8:
        sentences.append(_FILLER)
    return sentences[:8]
