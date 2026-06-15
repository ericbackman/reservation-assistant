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
> place the reservation.
>
> **V2 is human-in-the-loop, by design.** Resy/OpenTable access is unofficial and
> Terms-of-Service-restricted, so the agent never books. Instead it *watches* for
> a table you want and pings you the instant one opens, with a one-tap link to
> finish the booking yourself. There is deliberately no `book()` method anywhere —
> that keeps the tool clear of platform ToS and the reservation-reselling laws
> (which target commercialization, not personal use). See the provider stubs and
> `watch.py` for the full rationale.

## Quick start

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env        # paste your Google Places API key
python cli.py "date-night Italian" --area Ossington --price-max 3
```

## Getting a Google Places API key (free, ~5 min)

Costs $0 at personal volume, but **billing must be enabled** (a card on file) even
for the free tier, and you should **cap usage** so a bug can't run up a bill.

1. **Project** — [console.cloud.google.com](https://console.cloud.google.com) →
   project dropdown → New Project → select it.
2. **Billing** *(required even for free)* — ☰ → Billing → link/create a billing account.
3. **Enable** — APIs & Services → Library → **"Places API (New)"** → Enable.
   (Must be the **(New)** one — the legacy "Places API" won't match this code.)
4. **Key** — APIs & Services → Credentials → Create credentials → API key (`AIza…`).
5. **Restrict** — edit the key → API restrictions → restrict to **Places API (New)** only.
   (App restrictions: None for a local script.)
6. **Cap it** — APIs & Services → Places API (New) → Quotas → set per-day limit low
   (e.g. **500/day**). This is the real circuit breaker — it *stops* calls past the cap.
7. **Budget alert (optional)** — Billing → Budgets & alerts → $1 budget, email at 100%.
   Note: alerts only email you; the quota in step 6 is what hard-stops spending.
8. **Use it** — `Copy-Item .env.example .env`, paste the key after `GOOGLE_PLACES_API_KEY=`.

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
