"""Resy provider — V2 STUB, human-in-the-loop *monitor* shape (not wired into V1).

Resy holds most of Toronto's hard-to-book trendy rooms and, unlike OpenTable,
exposes live availability through a reverse-engineered API (the resy-booking-bot
ecosystem). We use that power for WATCHING, not booking.

Contract (human-in-the-loop):
  - supports_availability() -> True: Resy can report live open slots
  - find_availability(target) -> [Slot]: ONE poll; report matching open tables,
    each carrying a confirm_url deep link
  - There is no book(). The human taps Slot.confirm_url to complete the booking.

Why this shape instead of auto-booking:
  Resy access is unofficial and against its Terms, and runs under YOUR account.
  Keeping the agent on discovery + monitoring and the HUMAN on the transaction is
  the most defensible posture: it sidesteps the reservation-piracy laws (personal
  use, no reselling) and still solves the real pain — you get pinged the instant a
  hard table drops, then book it yourself in one tap.

"Using my name" / agency note:
  Booking runs under the account whose token you supply, with that name + card on
  file. THAT account holder eats any no-show / cancellation fee. Treat the
  credentials as an explicit, revocable grant of agency for personal family use
  only — never commercial, never reselling.

When you implement V2:
  - auth: exchange email/password for a durable token once (never store the pw)
  - find_availability(): hit Resy's /find for the venue/date/party window, map
    each open slot -> Slot(confirm_url=<resy deep link>, ...)
  - DO NOT add a book(). Wire Slot.confirm_url into the Notifier instead.
"""
from __future__ import annotations

from ..models import ReservationRequest, Restaurant, Slot, WatchTarget
from .base import ReservationProvider


class ResyProvider(ReservationProvider):
    name = "resy"

    def supports_availability(self) -> bool:
        return True  # Resy can report live openings (the reason to add it in V2)

    def search(self, request: ReservationRequest) -> list[Restaurant]:
        raise NotImplementedError(
            "Resy is a V2 provider. V1 discovery ships with Google Places. "
            "See this file's docstring for the human-in-the-loop plan."
        )

    def find_availability(self, target: WatchTarget) -> list[Slot]:
        raise NotImplementedError(
            "Resy availability monitoring is V2. When built, this returns open "
            "Slots with confirm_url deep links for the human to tap — it never books."
        )
