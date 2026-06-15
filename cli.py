#!/usr/bin/env python
"""Thin CLI the `find-table` skill shells out to.

The skill parses a family member's natural-language ask into these flags, runs
this, and formats the result. Humans can run it directly too:

    python cli.py "date-night Italian" --area Ossington --price-max 3 --min-rating 4.3
    python cli.py "best ramen near me" --open-now --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make `src/` importable without an install step (keeps V1 zero-setup).
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from reservation_assistant import (  # noqa: E402
    ReservationRequest,
    find_options,
    load_preferences,
)
from reservation_assistant.providers.google_places import MissingApiKey  # noqa: E402


def _load_dotenv() -> None:
    """Minimal .env reader so we don't add a dependency just for one key."""
    env = Path(__file__).resolve().parent / ".env"
    if not env.exists():
        return
    # utf-8-sig strips a BOM if Notepad/PowerShell added one when saving .env
    for line in env.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        import os
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def build_request(args: argparse.Namespace, prefs) -> ReservationRequest:
    return ReservationRequest(
        query=args.query,
        area=args.area,
        cuisine=args.cuisine,
        price_max=args.price_max if args.price_max is not None else prefs.price_ceiling,
        min_rating=args.min_rating
        if args.min_rating is not None
        else prefs.min_rating_floor,
        open_now=args.open_now,
        party_size=args.party or prefs.default_party_size,
        limit=args.limit,
    )


def render_text(options, prefs) -> str:
    if not options:
        return "No matching restaurants found. Try loosening price or rating filters."
    lines = []
    for i, opt in enumerate(options, 1):
        r = opt.restaurant
        head = f"{i}. {r.name}  ·  {r.price_glyphs}"
        if r.rating:
            head += f"  ·  {r.rating}★ ({r.rating_count or 0} reviews)"
        lines.append(head)
        if r.primary_type:
            lines.append(f"   {r.primary_type.replace('_', ' ')}")
        if r.address:
            lines.append(f"   {r.address}")
        if opt.reasons:
            lines.append(f"   why: {', '.join(opt.reasons)}")
        if r.booking_link:
            lines.append(f"   book: {r.booking_link}")
        lines.append("")
    if prefs.reservation_name:
        lines.append(f"(reservations would be held under: {prefs.reservation_name})")
    return "\n".join(lines).rstrip()


def render_json(options) -> str:
    payload = [
        {
            "name": o.restaurant.name,
            "type": o.restaurant.primary_type,
            "price_level": o.restaurant.price_level,
            "rating": o.restaurant.rating,
            "rating_count": o.restaurant.rating_count,
            "address": o.restaurant.address,
            "open_now": o.restaurant.open_now,
            "booking_link": o.restaurant.booking_link,
            "score": round(o.score, 4),
            "reasons": o.reasons,
        }
        for o in options
    ]
    return json.dumps(payload, indent=2)


def main() -> int:
    # Windows consoles default to cp1252 and crash on glyphs like ★ — force UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Toronto restaurant discovery (V1)")
    parser.add_argument("query", help="free-text ask, e.g. 'cozy Italian for a date'")
    parser.add_argument("--area", help="neighborhood to bias toward, e.g. Ossington")
    parser.add_argument("--cuisine", help="cuisine hint used in ranking, e.g. Italian")
    parser.add_argument("--price-max", type=int, choices=[1, 2, 3, 4])
    parser.add_argument("--min-rating", type=float)
    parser.add_argument("--open-now", action="store_true")
    parser.add_argument("--party", type=int, help="party size (recorded, not a V1 filter)")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    _load_dotenv()
    prefs = load_preferences()
    request = build_request(args, prefs)

    try:
        options = find_options(request, prefs)
    except MissingApiKey as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(render_json(options) if args.json else render_text(options, prefs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
