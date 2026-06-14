"""OpenTable provider — V2 STUB (not wired into V1).

OpenTable is broader than Resy but has NO official consumer API and its Terms
explicitly prohibit "automated assistants" and "AI technology." Existing tools
get around this by riding your signed-in browser session (a proxy/extension
bridge) so requests look human — brittle (internal query hashes rotate often)
and still ToS-risky. Treat this as the last/least-favored integration.

When you implement V2:
  - auth: import the user's own logged-in session cookies (no password flow)
  - search(): drive the live site / internal /dapi endpoints, normalize -> Restaurant
  - supports_booking(): return True only once you've accepted the risk above
"""
from __future__ import annotations

from ..models import ReservationRequest, Restaurant
from .base import ReservationProvider


class OpenTableProvider(ReservationProvider):
    name = "opentable"

    def supports_booking(self) -> bool:
        return True

    def search(self, request: ReservationRequest) -> list[Restaurant]:
        raise NotImplementedError(
            "OpenTable is a V2 provider with real ToS risk. V1 is Google Places only. "
            "See this file's docstring before enabling it."
        )
