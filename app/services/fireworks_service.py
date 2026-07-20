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
    team_a: list[Character], team_b: list[Character], winner: str
) -> list[str]:
    settings = get_settings()
    client = OpenAI(api_key=settings.fireworks_api_key, base_url=_BASE_URL)

    winner_team = team_a if winner == "A" else team_b
    loser_team = team_b if winner == "A" else team_a
    winner_label = "Team A" if winner == "A" else "Team B"
    loser_label = "Team B" if winner == "A" else "Team A"
    winner_names = ", ".join(c.name for c in winner_team)
    loser_names = ", ".join(c.name for c in loser_team)

    prompt = f"""You are a battle narrator. Two teams of comic book heroes/villains are fighting.

Team A:
{_format_team(team_a)}

Team B:
{_format_team(team_b)}

Outcome: {winner_label} ({winner_names}) wins. {loser_label} ({loser_names}) loses.

Write exactly 8 sentences narrating the battle. Follow this structure strictly:
- Sentences 1-2: Setup — the teams arrive and posture.
- Sentences 3-6: Escalating clash — attacks, counters, momentum swinging both ways.
- Sentence 7: The decisive blow — {winner_label} ({winner_names}) lands a specific, concrete winning strike that turns the fight.
- Sentence 8: The aftermath — {loser_label} ({loser_names}) falls or retreats; name {winner_label} ({winner_names}) as the victors.

Each sentence on its own line. Return only the 8 sentences, nothing else."""

    response = client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.8,
        extra_body={"reasoning_effort": "low"},
    )

    text = response.choices[0].message.content.strip()
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip())
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(flat) if s.strip()]
    while len(sentences) < 8:
        sentences.append(_FILLER)
    return sentences[:8]
