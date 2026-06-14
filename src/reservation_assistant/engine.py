"""The orchestration layer: request -> provider search -> hard filters -> rank.

This file deliberately stays thin and boring. The two pieces of real judgment
live elsewhere: WHERE to look (providers/) and HOW to rank (ranking.py — your
contribution). Everything here is plumbing between those two.
"""
from __future__ import annotations

from .models import RankedOption, ReservationRequest, Restaurant
from .preferences import Preferences
from .providers import ENABLED
from .providers.base import ReservationProvider
from .ranking import rank_options


def _passes_hard_filters(r: Restaurant, request: ReservationRequest) -> bool:
    """Drop anything that violates an explicit hard constraint BEFORE ranking.
    Soft preferences (favorite cuisines, etc.) are the ranker's job, not this."""
    if request.price_max is not None and r.price_level is not None:
        if r.price_level > request.price_max:
            return False
    if request.min_rating is not None and r.rating is not None:
        if r.rating < request.min_rating:
            return False
    if request.open_now and r.open_now is False:
        return False
    return True


def find_options(
    request: ReservationRequest,
    preferences: Preferences | None = None,
    providers: list[ReservationProvider] | None = None,
) -> list[RankedOption]:
    """Top-level entry point. Returns ranked options, best first."""
    preferences = preferences or Preferences()
    active = providers or [cls() for cls in ENABLED]

    # Fan out across providers and pool the candidates. V1 has one provider, but
    # de-duping by name keeps this honest once Resy + OpenTable both contribute.
    pooled: dict[str, Restaurant] = {}
    for provider in active:
        for r in provider.search(request):
            pooled.setdefault(r.name.lower(), r)

    candidates = [r for r in pooled.values() if _passes_hard_filters(r, request)]
    ranked = rank_options(candidates, request, preferences)
    return ranked[: request.limit]
