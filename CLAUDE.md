# reservation-assistant

A Toronto restaurant **reservation concierge** for Eric's family. A family member
describes what they want in plain language; the agent returns ranked, explainable
restaurant options with booking links.

## Status: V1 — discovery only

V1 **finds and recommends**; it does not book. The booking hand-off is a link.
Booking (Resy/OpenTable) is V2 and carries Terms-of-Service / account-ban risk —
see the docstrings in `src/reservation_assistant/providers/resy.py` and
`opentable.py` before enabling those providers.

## Architecture

```
find-table skill (NL → filters)        .claude/skills/find-table/SKILL.md
        │
        ▼
cli.py  ──►  engine.find_options()     orchestration: search → filter → rank
                 │            │
                 │            └─►  ranking.rank_options()   ← family's taste (yours to tune)
                 ▼
        providers/ (behind ReservationProvider)
          • GooglePlacesProvider  ✅ V1, official API, discovery only
          • ResyProvider          ⏸ V2 stub, availability monitor (no book())
          • OpenTableProvider     ⏸ V2 stub, availability monitor (no book())

V2 — human-in-the-loop (watch.py):

  WatchTarget ─► provider.find_availability() ─► should_notify() ─► Notifier
                      (open Slots)               (your policy)      (one-tap link)

  The agent REPORTS open tables; the HUMAN taps Slot.confirm_url to book.
  There is deliberately no book() anywhere — that boundary is the design, and
  it's what keeps the tool on the clean side of platform ToS + reservation law.
```

The engine depends only on the `ReservationProvider` interface — adding a
platform is a new subclass, never a rewrite.

## Setup

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env      # then paste your Google Places API key into .env
```

## Run

```powershell
python cli.py "cozy Italian for a date" --area Ossington --price-max 3
python cli.py "best ramen in Toronto" --open-now --json
```

## The three human-owned decisions

1. **`src/reservation_assistant/ranking.py`** — how options get scored. Encodes
   what the family values when good spots tie (rating vs price-fit vs novelty).
2. **`config/preferences.toronto.json`** — the family's standing taste (cuisines,
   areas, price ceiling, the reservation name). Fill the `TODO` markers.
3. **`src/reservation_assistant/watch.py` → `should_notify()`** (V2) — when an
   open table is actually worth pinging a human about (dedup, time window, quiet
   hours, prime-time-only). Tunes how the monitor interrupts your family.

## Conventions

- Branch naming: `feature/*`, `fix/*`, `chore/*`
- Conventional commits (`feat:`, `fix:`, `refactor:`, ...)
- Never commit `.env` or API keys
- Windows / PowerShell; Python 3.10+ (uses `X | Y` type unions)
```
