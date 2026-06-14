"""Google Places API (New) — the V1 discovery provider.

Official, sanctioned, free tier. No Terms-of-Service grey area: this is a public
API you hold a key for. It does NOT expose live table availability — that lives
behind Resy/OpenTable — so this provider is discovery-only and hands off a
booking link. See providers/resy.py + providers/opentable.py for the V2 stubs.

Docs: https://developers.google.com/maps/documentation/places/web-service/text-search
"""
from __future__ import annotations

import os

import requests

from ..models import PRICE_LEVEL_MAP, ReservationRequest, Restaurant
from .base import ReservationProvider

# Bias results toward Toronto so "Italian near Ossington" doesn't return Milan.
# (lat, lng, radius_metres) — central Toronto, ~15km covers the GTA core.
TORONTO_CENTER = {"latitude": 43.6532, "longitude": -79.3832}
TORONTO_RADIUS_M = 15000

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Only pay for the fields we use — the field mask is billed, so keep it tight.
FIELD_MASK = ",".join(
    f"places.{f}"
    for f in (
        "displayName",
        "primaryType",
        "priceLevel",
        "rating",
        "userRatingCount",
        "formattedAddress",
        "currentOpeningHours.openNow",
        "currentOpeningHours.weekdayDescriptions",
        "websiteUri",
        "googleMapsUri",
        "reservable",
        "id",
    )
)


class MissingApiKey(RuntimeError):
    """Raised when GOOGLE_PLACES_API_KEY isn't set — keeps the failure obvious."""


class GooglePlacesProvider(ReservationProvider):
    name = "google_places"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GOOGLE_PLACES_API_KEY")

    # discovery only: inherits supports_availability() -> False and
    # find_availability() -> [] from the base class. V1 hands off a link.

    def search(self, request: ReservationRequest) -> list[Restaurant]:
        if not self.api_key:
            raise MissingApiKey(
                "Set GOOGLE_PLACES_API_KEY (copy .env.example to .env and add your key). "
                "Get one free at https://console.cloud.google.com/ → enable 'Places API (New)'."
            )

        text_query = request.query
        if request.area and request.area.lower() not in text_query.lower():
            text_query = f"{text_query} in {request.area}, Toronto"
        elif "toronto" not in text_query.lower():
            text_query = f"{text_query}, Toronto"

        body: dict = {
            "textQuery": text_query,
            "includedType": "restaurant",
            "locationBias": {
                "circle": {"center": TORONTO_CENTER, "radius": TORONTO_RADIUS_M}
            },
            "maxResultCount": 20,  # over-fetch; the engine filters + the ranker trims
        }
        if request.open_now:
            body["openNow"] = True
        if request.min_rating:
            body["minRating"] = request.min_rating

        resp = requests.post(
            TEXT_SEARCH_URL,
            json=body,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": FIELD_MASK,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return [self._to_restaurant(p) for p in resp.json().get("places", [])]

    def _to_restaurant(self, p: dict) -> Restaurant:
        hours = p.get("currentOpeningHours", {})
        return Restaurant(
            name=p.get("displayName", {}).get("text", "Unknown"),
            source=self.name,
            primary_type=p.get("primaryType"),
            price_level=PRICE_LEVEL_MAP.get(p.get("priceLevel")),
            rating=p.get("rating"),
            rating_count=p.get("userRatingCount"),
            address=p.get("formattedAddress"),
            open_now=hours.get("openNow"),
            hours=hours.get("weekdayDescriptions", []),
            website_uri=p.get("websiteUri"),
            maps_uri=p.get("googleMapsUri"),
            reservable=p.get("reservable"),
            provider_id=p.get("id"),
        )
