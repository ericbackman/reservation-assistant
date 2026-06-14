"""The contract every reservation provider must satisfy.

The whole point of this interface: the engine depends on `ReservationProvider`,
never on Google/Resy/OpenTable directly. Swapping or adding a platform is a new
subclass, not a rewrite. V1 ships exactly one concrete provider (Google Places,
discovery-only); V2 will add Resy/OpenTable subclasses that also book.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import ReservationRequest, Restaurant, Slot, WatchTarget


class ReservationProvider(ABC):
    #: short stable id, also stored on each Restaurant.source
    name: str = "base"

    @abstractmethod
    def search(self, request: ReservationRequest) -> list[Restaurant]:
        """Return candidate restaurants for the request. Discovery only —
        ranking and filtering happen downstream in the engine."""

    def booking_link(self, restaurant: Restaurant) -> str | None:
        """A generic per-restaurant link a human can click to go book themselves
        (used by V1 discovery hand-off)."""
        return restaurant.booking_link

    # --- V2: human-in-the-loop availability monitoring -----------------------
    # NOTE: there is deliberately NO book() method anywhere in this hierarchy.
    # A provider may REPORT open tables; only the human completes the booking, via
    # Slot.confirm_url. That boundary is the entire point of the design — the code
    # structurally cannot place a reservation on its own.
    def supports_availability(self) -> bool:
        """Whether this provider can report live open slots (V2). Discovery-only
        providers (e.g. Google Places) return False."""
        return False

    def find_availability(self, target: WatchTarget) -> list[Slot]:
        """One poll for open tables matching `target`. Default: empty, because
        discovery providers have no live availability. V2 providers override and
        return Slots that each carry a confirm_url for the human to tap."""
        return []
