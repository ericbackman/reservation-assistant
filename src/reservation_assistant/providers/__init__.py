"""Provider registry.

Only providers listed in ENABLED are used by the engine. V1 enables Google
Places alone — the Resy/OpenTable classes exist so the architecture is visible
and the V2 path is obvious, but they stay out of ENABLED until intentionally
turned on (and their ToS trade-offs accepted).
"""
from .base import ReservationProvider
from .google_places import GooglePlacesProvider
from .opentable import OpenTableProvider
from .resy import ResyProvider

# The active provider for V1. A list, not a single value, so the engine can fan
# out across multiple platforms later (Resy holds different rooms than OpenTable).
ENABLED: list[type[ReservationProvider]] = [GooglePlacesProvider]

__all__ = [
    "ReservationProvider",
    "GooglePlacesProvider",
    "ResyProvider",
    "OpenTableProvider",
    "ENABLED",
]
