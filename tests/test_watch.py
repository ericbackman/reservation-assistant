"""Smoke tests for the human-in-the-loop watch flow — no network, no API key.

A fake provider returns two slots (one in-window, one too late); we assert the
watcher only pings for acceptable, not-yet-seen slots, and that a discovery-only
provider refuses to watch. Run: `python tests/test_watch.py`
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reservation_assistant.models import Slot, WatchTarget
from reservation_assistant.providers.base import ReservationProvider
from reservation_assistant.providers.google_places import GooglePlacesProvider
from reservation_assistant.watch import Notifier, run_watch


class RecordingNotifier(Notifier):
    """Captures alerts instead of printing, so tests can assert on them."""

    def __init__(self):
        self.sent: list[str] = []

    def notify(self, slot, target):
        self.sent.append(slot.key())


class FakeWatchProvider(ReservationProvider):
    name = "fake_watch"

    def search(self, request):
        return []

    def supports_availability(self):
        return True

    def find_availability(self, target):
        return [
            Slot(restaurant_name="Alo", source=self.name, date="2026-06-21",
                 time="19:30", party_size=2, confirm_url="https://resy.test/alo"),
            Slot(restaurant_name="Alo", source=self.name, date="2026-06-21",
                 time="22:45", party_size=2, confirm_url="https://resy.test/alo-late"),
        ]


TARGET = WatchTarget(
    restaurant_name="Alo", provider="fake_watch", date="2026-06-21",
    party_size=2, earliest_time="18:00", latest_time="21:00",
)


def test_notifies_only_in_window():
    notifier = RecordingNotifier()
    fired = run_watch(TARGET, FakeWatchProvider(), notifier=notifier)
    assert len(fired) == 1, f"expected 1 in-window slot, got {len(fired)}"
    assert fired[0].time == "19:30", "the 22:45 slot is outside the window and should be skipped"
    assert len(notifier.sent) == 1


def test_dedup_across_polls():
    notifier = RecordingNotifier()
    seen: set[str] = set()
    run_watch(TARGET, FakeWatchProvider(), notifier=notifier, already_notified=seen)
    run_watch(TARGET, FakeWatchProvider(), notifier=notifier, already_notified=seen)
    assert len(notifier.sent) == 1, "second poll must not re-notify the same slot"


def test_discovery_provider_cannot_watch():
    # supports_availability() is False -> run_watch refuses BEFORE any network call.
    try:
        run_watch(TARGET, GooglePlacesProvider(api_key="dummy"), notifier=RecordingNotifier())
    except ValueError:
        return
    raise AssertionError("expected ValueError for a discovery-only provider")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL  {name}: {e}")
    print(f"\n{'ALL TESTS PASSED' if not failures else f'{failures} FAILURE(S)'}")
    raise SystemExit(1 if failures else 0)
