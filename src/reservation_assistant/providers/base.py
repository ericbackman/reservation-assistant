"""The contract every reservation provider must satisfy.

The whole point of this interface: the engine depends on `ReservationProvider`,
never on Google/Resy/OpenTable directly. Swapping or adding a platform is a new
subclass, not a rewrite. V1 ships exactly one concrete provider (Google Places,
discovery-only); V2 will add Resy/OpenTable subclasses that also book.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import ReservationRequest, Restaurant


class ReservationProvider(ABC):
    #: short stable id, also stored on each Restaurant.source
    name: str = "base"

    @abstractmethod
    def search(self, request: ReservationRequest) -> list[Restaurant]:
        """Return candidate restaurants for the request. Discovery only —
        ranking and filtering happen downstream in the engine."""

    def supports_booking(self) -> bool:
        """Whether this provider can actually hold/book a table (V2). Discovery
        providers return False; the engine uses this to decide whether to offer
        a 'book here' hand-off link vs. an in-agent booking flow."""
        return False

    def booking_link(self, restaurant: Restaurant) -> str | None:
        """A URL a human can click to finish the reservation themselves."""
        return restaurant.booking_link
