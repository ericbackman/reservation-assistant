"""Human-in-the-loop reservation monitoring (V2 orchestration).

The agent's job ends at: "a table you want just opened — here's the one-tap link."
A human always completes the booking. This module is the plumbing for that:

    poll a provider for availability  ->  decide what's worth a ping  ->  notify

What it deliberately does NOT do: complete a reservation. There is no booking call
here or in any provider — the human taps Slot.confirm_url. See providers/resy.py
for the rationale (ToS, agency, no-show liability).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Slot, WatchTarget
from .providers.base import ReservationProvider


class Notifier(ABC):
    """How a human gets pinged when a table opens.

    Console today; push / SMS / a Discord DM to your sister tomorrow are just new
    subclasses — the watcher never needs to know which.
    """

    @abstractmethod
    def notify(self, slot: Slot, target: WatchTarget) -> None:
        ...


class ConsoleNotifier(Notifier):
    """Prints the alert. ASCII-only so it never trips Windows console encoding."""

    def notify(self, slot: Slot, target: WatchTarget) -> None:
        link = slot.confirm_url or "(no link available)"
        print(
            f"[TABLE OPEN] {slot.restaurant_name} - {slot.date} {slot.time} "
            f"for {slot.party_size}\n  tap to book: {link}"
        )


def should_notify(
    slot: Slot, target: WatchTarget, already_notified: set[str]
) -> bool:
    """CONTRIBUTION POINT (3 of 3): when is an open table worth pinging a human?

    The naive answer ("any open slot") spams. The real judgment lives here:
      - dedup:   never ping twice for the same slot (slot.key() + already_notified)
      - window:  only slots inside the human's earliest/latest_time
      - quality: maybe only ping prime times? or escalate — quiet at 5pm, loud at
                 7:30? or only the FIRST acceptable slot per night, not every wiggle?
      - quiet hours: don't buzz someone at 3am even if a table drops

    Return True to fire the notifier. The caller records slot.key() into
    `already_notified` when you do, so the next poll won't re-ping the same table.

    TODO(eric): tune this to how your family actually wants to be interrupted.
    The placeholder below = dedup + inside the requested window.
    """
    if slot.key() in already_notified:
        return False
    if not target.in_window(slot.time):
        return False
    return True


def run_watch(
    target: WatchTarget,
    provider: ReservationProvider,
    notifier: Notifier | None = None,
    already_notified: set[str] | None = None,
) -> list[Slot]:
    """Run ONE availability poll and notify on anything worth pinging.

    Returns the slots that triggered a notification. Cadence (poll every N minutes
    until the date passes) is intentionally left to an outside runner/cron — this
    stays a single, testable, side-effect-light step. A long-lived loop is a
    deployment concern, not a logic concern.

    Pass a persistent `already_notified` set across calls to get cross-poll dedup.
    """
    if not provider.supports_availability():
        raise ValueError(
            f"{provider.name} is discovery-only; it can't monitor availability. "
            "Use a V2 provider (Resy/OpenTable) for watching."
        )

    notifier = notifier or ConsoleNotifier()
    seen = already_notified if already_notified is not None else set()

    fired: list[Slot] = []
    for slot in provider.find_availability(target):
        if should_notify(slot, target, seen):
            notifier.notify(slot, target)
            seen.add(slot.key())
            fired.append(slot)
    return fired
