"""Resy provider — V2 STUB (not wired into V1).

Resy holds most of Toronto's hard-to-book trendy rooms, and unlike OpenTable it
exposes live availability + booking through a reverse-engineered API (see the
resy-booking-bot ecosystem). That power comes with risk: it is unofficial and
against Resy's Terms; actions run under YOUR logged-in account. Keep this
disabled until you've decided you're comfortable with that trade-off.

When you implement V2:
  - auth: exchange email/password for a durable token once (never store the pw)
  - search(): hit Resy's /find endpoint, normalize venues -> Restaurant
  - supports_booking(): return True, and add a book(restaurant, slot) method
"""
from __future__ import annotations

from ..models import ReservationRequest, Restaurant
from .base import ReservationProvider


class ResyProvider(ReservationProvider):
    name = "resy"

    def supports_booking(self) -> bool:
        return True  # the whole reason to add Resy later

    def search(self, request: ReservationRequest) -> list[Restaurant]:
        raise NotImplementedError(
            "Resy is a V2 provider. Discovery-only V1 ships with Google Places. "
            "See this file's docstring for the implementation plan and the ToS caveat."
        )
