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
          • ResyProvider          ⏸ V2 stub (booking, ToS-risky)
          • OpenTableProvider     ⏸ V2 stub (booking, ToS-risky)
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

## The two human-owned decisions

1. **`src/reservation_assistant/ranking.py`** — how options get scored. Encodes
   what the family values when good spots tie (rating vs price-fit vs novelty).
2. **`config/preferences.toronto.json`** — the family's standing taste (cuisines,
   areas, price ceiling, the reservation name). Fill the `TODO` markers.

## Conventions

- Branch naming: `feature/*`, `fix/*`, `chore/*`
- Conventional commits (`feat:`, `fix:`, `refactor:`, ...)
- Never commit `.env` or API keys
- Windows / PowerShell; Python 3.10+ (uses `X | Y` type unions)
```
