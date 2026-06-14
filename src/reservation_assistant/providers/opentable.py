"""OpenTable provider — V2 STUB, human-in-the-loop *monitor* shape (not wired into V1).

OpenTable is broader than Resy but has NO official consumer API, and its Terms
explicitly prohibit "robot, spider, scraper, generative AI or other AI technology."
Existing tools get around this by riding your signed-in browser session so requests
look human — brittle (internal query hashes rotate often) and the least-favored
integration. Use it only for WATCHING, never booking.

Contract (human-in-the-loop):
  - supports_availability() -> True: can report open slots (via the live site)
  - find_availability(target) -> [Slot]: ONE poll; report matching open tables,
    each carrying a confirm_url deep link
  - There is no book(). The human taps Slot.confirm_url to complete the booking.

"Using my name" / agency note:
  Same as Resy — the reservation lands under the session's account/name/card, and
  that person owns any no-show fee. Personal family use only; no reselling (that's
  what the reservation-piracy laws actually target).

When you implement V2:
  - auth: import the user's own logged-in session cookies (no password flow)
  - find_availability(): drive the live site / internal /dapi endpoints for the
    venue/date/party window, map open slots -> Slot(confirm_url=<deep link>, ...)
  - DO NOT add a book(). Surface Slot.confirm_url through the Notifier instead.
"""
from __future__ import annotations

from ..models import ReservationRequest, Restaurant, Slot, WatchTarget
from .base import ReservationProvider


class OpenTableProvider(ReservationProvider):
    name = "opentable"

    def supports_availability(self) -> bool:
        return True

    def search(self, request: ReservationRequest) -> list[Restaurant]:
        raise NotImplementedError(
            "OpenTable is a V2 provider with real ToS friction. V1 is Google Places only. "
            "See this file's docstring before enabling it."
        )

    def find_availability(self, target: WatchTarget) -> list[Slot]:
        raise NotImplementedError(
            "OpenTable availability monitoring is V2. When built, this returns open "
            "Slots with confirm_url deep links for the human to tap — it never books."
        )
