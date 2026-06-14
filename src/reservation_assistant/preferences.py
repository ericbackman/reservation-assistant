"""Loads the family's standing preferences from config/preferences.toronto.json.

This is the "memory" that lets a request stay short ("date-night Italian") while
still respecting that, say, the family avoids loud rooms and tops out at $$$.
The ranker reads these to nudge scores. The actual values are YOUR domain
knowledge — see the JSON file's TODO markers.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PROFILE = (
    Path(__file__).resolve().parents[2] / "config" / "preferences.toronto.json"
)


@dataclass
class Preferences:
    reservation_name: str = ""          # whose name reservations are held under
    default_party_size: int = 2
    price_ceiling: int | None = None    # 1-4; soft cap the ranker discourages exceeding
    favorite_cuisines: list[str] = field(default_factory=list)
    avoid_cuisines: list[str] = field(default_factory=list)
    favorite_areas: list[str] = field(default_factory=list)
    min_rating_floor: float | None = None
    notes: str = ""                     # free text, surfaced to the user for context

    @classmethod
    def from_dict(cls, data: dict) -> "Preferences":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


def load_preferences(path: Path | str | None = None) -> Preferences:
    """Load the profile, falling back to empty defaults if the file is missing
    so the engine still runs on a fresh checkout."""
    p = Path(path) if path else DEFAULT_PROFILE
    if not p.exists():
        return Preferences()
    return Preferences.from_dict(json.loads(p.read_text(encoding="utf-8")))
