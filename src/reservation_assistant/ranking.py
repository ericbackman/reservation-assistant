"""Ranking — how candidate restaurants get ordered into recommendations.

>>> THIS IS YOUR CONTRIBUTION POINT (1 of 2). <<<

The engine has already done discovery and dropped anything that fails a HARD
constraint (over the price ceiling, under the rating floor, closed when "open
now" was asked). What's left is a pool of valid candidates. Your job: turn the
SOFT signals into a single score so the best option floats to the top.

Why this is the interesting decision and not boilerplate:
  When two great spots tie, what wins? A family that optimizes for "never have a
  bad meal" weights rating + review_count heavily. One that optimizes for
  "discover new neighborhoods" weights area novelty. One that's budget-conscious
  rewards coming in UNDER the price ceiling. There's no universally right answer
  — it encodes your family's taste, which is exactly why you should write it.

Signals available to you (all optional / may be None):
  - r.rating (0-5), r.rating_count (more reviews = more trustworthy rating)
  - r.price_level (1-4) vs request.price_max / preferences.price_ceiling
  - r.primary_type (e.g. "italian_restaurant") vs request.cuisine /
    preferences.favorite_cuisines / preferences.avoid_cuisines
  - r.area vs preferences.favorite_areas
  - r.open_now, r.reservable

Return a list of RankedOption(restaurant, score, reasons), sorted best-first.
Push human-readable strings into `reasons` — the assistant shows them to explain
each pick ("4.8★ from 2,100 reviews", "in your price range", "matches Italian").
"""
from __future__ import annotations

from .models import RankedOption, ReservationRequest, Restaurant
from .preferences import Preferences


# ---- helpers you may find useful (use them or ignore them) -------------------

def _norm_rating(r: Restaurant) -> float:
    """Rating on a 0-1 scale; unrated places get a neutral 0.5."""
    return (r.rating / 5.0) if r.rating is not None else 0.5


def _matches_cuisine(r: Restaurant, names: list[str]) -> bool:
    """True if any cuisine name appears in the place's primary type."""
    t = (r.primary_type or "").lower()
    return any(name.lower() in t for name in names if name)


# ---- the function you write --------------------------------------------------

def rank_options(
    restaurants: list[Restaurant],
    request: ReservationRequest,
    preferences: Preferences,
) -> list[RankedOption]:
    """Score and sort candidates. Best option first.

    TODO(eric): Replace the placeholder below with your real scoring logic.
    A reasonable shape (feel free to diverge):

        scored = []
        for r in restaurants:
            score = 0.0
            reasons = []
            # 1. base quality — rating, but trust it more with many reviews
            # 2. price fit — reward at/under preferences.price_ceiling
            # 3. cuisine fit — boost favorite_cuisines / request.cuisine,
            #    penalize avoid_cuisines
            # 4. area fit — boost preferences.favorite_areas
            # ...append a human reason string each time a signal fires
            scored.append(RankedOption(r, score, reasons))
        return sorted(scored, key=lambda o: o.score, reverse=True)

    Think about: how much should review COUNT matter vs the star value? Should a
    place UNDER budget beat one at the ceiling, or is that a wash? Is matching
    cuisine a tiebreaker or a hard preference?
    """
    # --- placeholder so the pipeline runs before you write the real thing -----
    placeholder = [
        RankedOption(
            restaurant=r,
            score=_norm_rating(r),
            reasons=[f"{r.rating}★" if r.rating else "unrated", "(placeholder ranking)"],
        )
        for r in restaurants
    ]
    return sorted(placeholder, key=lambda o: o.score, reverse=True)
