"""Core data types shared across the reservation assistant.

These are intentionally provider-agnostic. A `Restaurant` looks the same whether
it came from Google Places (V1) or Resy/OpenTable (V2) — the providers are
responsible for translating their own API shapes into these objects.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# Google Places (New) returns price as an enum string; map it to a 1-4 int so
# ranking and filtering can do simple numeric comparisons. None = unknown.
PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}


@dataclass
class ReservationRequest:
    """A normalized ask. The `find-table` skill turns free text from a family
    member into one of these before calling the engine."""

    query: str                          # free-text, passed to the discovery provider
    area: Optional[str] = None          # neighborhood, e.g. "Ossington" — biases the search
    cuisine: Optional[str] = None       # e.g. "Italian" — used as a soft ranking signal
    price_max: Optional[int] = None     # 1-4 hard ceiling; None = no ceiling
    min_rating: Optional[float] = None  # hard floor on star rating
    open_now: bool = False              # only return places open right now
    party_size: Optional[int] = None    # recorded for context + V2 booking; not a V1 filter
    limit: int = 5                      # how many options to return

    def describe(self) -> str:
        bits = [self.query]
        if self.area:
            bits.append(f"in {self.area}")
        if self.price_max:
            bits.append("$" * self.price_max + " or under")
        if self.min_rating:
            bits.append(f"{self.min_rating}+ stars")
        return " · ".join(bits)


@dataclass
class Restaurant:
    """A single candidate, normalized from whatever provider produced it."""

    name: str
    source: str                         # which provider produced this ("google_places", ...)
    primary_type: Optional[str] = None  # e.g. "italian_restaurant"
    price_level: Optional[int] = None   # 1-4, see PRICE_LEVEL_MAP
    rating: Optional[float] = None       # 0-5 stars
    rating_count: Optional[int] = None   # number of reviews backing the rating
    address: Optional[str] = None
    area: Optional[str] = None
    open_now: Optional[bool] = None
    hours: list[str] = field(default_factory=list)  # human-readable weekly hours
    website_uri: Optional[str] = None    # the restaurant's own site (often the booking link)
    maps_uri: Optional[str] = None       # google maps fallback link
    reservable: Optional[bool] = None    # Google's hint that the place takes reservations
    provider_id: Optional[str] = None    # opaque id for follow-up calls (V2 booking)

    @property
    def price_glyphs(self) -> str:
        return "$" * self.price_level if self.price_level else "$?"

    @property
    def booking_link(self) -> Optional[str]:
        return self.website_uri or self.maps_uri


@dataclass
class RankedOption:
    """A restaurant plus the score and human-readable reasons the ranker gave it.

    The `reasons` list is what makes the assistant feel smart — surface it to the
    user so a recommendation is explainable ("4.8 stars, in your price range,
    matches Italian") rather than a black box.
    """

    restaurant: Restaurant
    score: float
    reasons: list[str] = field(default_factory=list)
