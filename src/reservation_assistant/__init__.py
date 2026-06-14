"""Reservation Assistant — Toronto restaurant discovery agent (V1).

Public surface:
    from reservation_assistant import find_options, ReservationRequest, load_preferences
"""
from .engine import find_options
from .models import RankedOption, ReservationRequest, Restaurant, Slot, WatchTarget
from .preferences import Preferences, load_preferences
from .watch import ConsoleNotifier, Notifier, run_watch, should_notify

__all__ = [
    # V1 discovery
    "find_options",
    "ReservationRequest",
    "Restaurant",
    "RankedOption",
    "Preferences",
    "load_preferences",
    # V2 human-in-the-loop monitoring
    "WatchTarget",
    "Slot",
    "run_watch",
    "should_notify",
    "Notifier",
    "ConsoleNotifier",
]
