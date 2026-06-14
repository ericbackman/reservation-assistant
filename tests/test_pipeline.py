"""Smoke tests for the discovery pipeline — no network, no API key needed.

Injects a fake provider so we exercise engine filtering + ranking deterministically.
Run: `python tests/test_pipeline.py`  (plain python, no pytest dependency)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reservation_assistant import ReservationRequest, find_options
from reservation_assistant.models import Restaurant
from reservation_assistant.providers.base import ReservationProvider


class FakeProvider(ReservationProvider):
    name = "fake"

    def search(self, request):
        return [
            Restaurant(name="Alo", source="fake", primary_type="french_restaurant",
                       price_level=4, rating=4.8, rating_count=2100, area="Queen W"),
            Restaurant(name="Cheap Eats", source="fake", primary_type="diner",
                       price_level=1, rating=3.9, rating_count=120),
            Restaurant(name="Edulis", source="fake", primary_type="spanish_restaurant",
                       price_level=4, rating=4.7, rating_count=900),
            Restaurant(name="Budget Gem", source="fake", primary_type="cafe",
                       price_level=2, rating=4.6, rating_count=300),
        ]


def test_rating_floor_filters():
    req = ReservationRequest(query="dinner", min_rating=4.0, limit=10)
    opts = find_options(req, providers=[FakeProvider()])
    assert all(o.restaurant.rating >= 4.0 for o in opts), "rating floor not applied"
    assert "Cheap Eats" not in [o.restaurant.name for o in opts], "3.9★ should be dropped"


def test_price_ceiling_filters():
    req = ReservationRequest(query="dinner", price_max=2, limit=10)
    opts = find_options(req, providers=[FakeProvider()])
    names = [o.restaurant.name for o in opts]
    assert "Alo" not in names and "Edulis" not in names, "$$$$ should be dropped at price_max=2"
    assert "Budget Gem" in names, "$$ should survive price_max=2"


def test_limit_respected():
    req = ReservationRequest(query="dinner", limit=2)
    opts = find_options(req, providers=[FakeProvider()])
    assert len(opts) == 2, f"expected 2, got {len(opts)}"


def test_sorted_best_first():
    req = ReservationRequest(query="dinner", limit=10)
    opts = find_options(req, providers=[FakeProvider()])
    scores = [o.score for o in opts]
    assert scores == sorted(scores, reverse=True), "options not sorted best-first"


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
