# 🍽️ reservation-assistant

A natural-language **restaurant concierge for Toronto**. Ask in plain English —
*"somewhere nice and Italian in Ossington for Saturday"* — and get back a short,
ranked, explainable list of options with booking links.

Built as a Claude Code skill on top of a small, provider-abstracted Python engine.

## What it does (V1)

- Parses a free-text ask into structured filters (cuisine, area, price, rating)
- Queries the **Google Places API (New)** — official, sanctioned, free tier
- Filters on hard constraints, then ranks on the family's taste
- Returns the top options, each with *why it was picked* and a booking link

> **V1 is discovery only.** It recommends and hands off a link — it does not
> place the reservation. Live availability + booking (Resy/OpenTable) is V2 and
> involves unofficial, Terms-of-Service-restricted access; the provider stubs
> document that path and its risks.

## Quick start

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env        # paste your Google Places API key
python cli.py "date-night Italian" --area Ossington --price-max 3
```

## Architecture

The engine talks to a `ReservationProvider` interface, not to any specific
platform — so Google (V1), Resy, and OpenTable (V2) are interchangeable modules.
See [`CLAUDE.md`](CLAUDE.md) for the diagram and the two human-owned decision
points (`ranking.py`, `config/preferences.toronto.json`).

## Why no official booking API?

Neither OpenTable nor Resy offers a sanctioned consumer reservation API. Every
booking tool in the wild reverse-engineers private endpoints or rides your
logged-in browser session — against their Terms, with your account bearing the
risk. This project keeps the clean, durable discovery layer separate from that
decision so V1 ships safely.
