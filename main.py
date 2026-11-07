"""Public SWGOH.GG profile sync API for SWGOH Tracker.

Render entry point: main:app
This service only reads public profile/roster pages. It does not expose private inventory.
"""
import asyncio
import json
import os
import re
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_VERSION = "0.6-backend"
SWGOH_GG_BASE = os.getenv("SWGOH_GG_BASE", "https://swgoh.gg").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "25"))
USER_AGENT = os.getenv(
    "SWGOH_GG_USER_AGENT",
    "Mozilla/5.0 (compatible; SWGOH-Tracker/0.6; public profile sync)",
)

DEFAULT_ORIGINS = [
    "https://jimmyhzz1.github.io",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", ",".join(DEFAULT_ORIGINS)).split(",")
    if origin.strip()
]

app = FastAPI(
    title="SWGOH Tracker Sync API",
    version=APP_VERSION,
    description="Reads public SWGOH.GG profile and character pages only.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class SyncRequest(BaseModel):
    allyCode: str = Field(..., description="Nine-digit SWGOH ally code")


def clean_code(value: str) -> str:
    code = re.sub(r"\D", "", value or "")
    if len(code) != 9:
        raise HTTPException(status_code=400, detail="Ally Code must contain exactly 9 digits.")
    return code


def _number(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d[\d,]*", value)
    return int(match.group(0).replace(",", "")) if match else None


def parse_profile(html: str, code: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    profile: dict[str, Any] = {"allyCode": code}

    patterns = [
        r"Galactic Power\s*[:：]?\s*([\d,]+)",
        r"Total GP\s*[:：]?\s*([\d,]+)",
        r"([\d,]+)\s*Galactic Power",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            profile["gp"] = int(match.group(1).replace(",", ""))
            break

    for pattern in (r"(\d+)\s+units", r"Units\s*[:：]?\s*(\d+)"):
        match = re.search(pattern, text, re.I)
        if match:
            profile["rosterCount"] = int(match.group(1))
            break

    # Preserve a display name when SWGOH.GG exposes one in the page title.
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if title:
        profile["name"] = re.sub(r"\s*[|–-]\s*SWGOH\.GG.*$", "", title, flags=re.I).strip()
    return profile


def _normalise_unit_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", value or "")


def parse_roster(html: str) -> list[dict[str, Any]]:
    """Extract roster rows conservatively from public character-page markup."""
    soup = BeautifulSoup(html, "html.parser")
    units: dict[str, dict[str, Any]] = {}

    # Structured attributes, if SWGOH.GG includes them in the rendered page.
    for node in soup.select("[data-unit-id], [data-definition-id]"):
        unit_id = _normalise_unit_id(node.get("data-unit-id") or node.get("data-definition-id") or "")
        name = node.get("data-unit-name") or node.get("aria-label") or node.get_text(" ", strip=True)
        if unit_id and name:
            units[unit_id] = {"id": unit_id, "name": name.strip()[:120]}

    # Character detail links are a useful fallback on the public /characters/ page.
    for link in soup.select('a[href*="/characters/"]'):
        href = link.get("href", "")
        match = re.search(r"/characters/([^/?#]+)/?", href)
        if not match:
            continue
        slug = _normalise_unit_id(match.group(1))
        if not slug:
            continue

        container = link
        for _ in range(4):
            if container.parent and getattr(container.parent, "name", None) not in ("body", "html"):
                container = container.parent
            else:
                break

        name = link.get_text(" ", strip=True)
        if not name:
            image = container.find("img")
            name = (image.get("alt") or image.get("title") or "") if image else ""
        if not name:
            heading = container.find(["h1", "h2", "h3", "h4"])
            name = heading.get_text(" ", strip=True) if heading else ""
        if not name:
            continue

        item: dict[str, Any] = {"id": slug, "name": name.strip()[:120]}
        card_text = container.get_text(" ", strip=True)
        gear = re.search(r"(?:Gear|G)\s*(?:Level)?\s*[:#]?\s*(\d{1,2})", card_text, re.I)
        relic = re.search(r"(?:Relic|R)\s*(?:Level)?\s*[:#]?\s*(\d{1,2})", card_text, re.I)
        if gear:
            item["currentTier"] = int(gear.group(1))
        if relic:
            item["relicTier"] = int(relic.group(1))
        units.setdefault(slug, item)

    # Some versions expose roster data as embedded JSON.
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or script.get_text())
        except (json.JSONDecodeError, TypeError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            name = candidate.get("name")
            identifier = candidate.get("identifier") or candidate.get("@id")
            if name and identifier:
                unit_id = _normalise_unit_id(str(identifier).rstrip("/").split("/")[-1])
                if unit_id:
                    units.setdefault(unit_id, {"id": unit_id, "name": str(name)[:120]})

    return list(units.values())


async def fetch_page(client: httpx.AsyncClient, url: str, label: str) -> str:
    try:
        response = await client.get(url)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"SWGOH.GG {label} page was not found for this Ally Code.")
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", "").lower():
            raise HTTPException(status_code=502, detail=f"SWGOH.GG returned an unexpected response for the {label} page.")
        return response.text
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Timed out contacting SWGOH.GG for the {label} page.")
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        raise HTTPException(status_code=502, detail=f"SWGOH.GG returned HTTP {status} while loading the {label} page.")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail=f"Could not connect to SWGOH.GG while loading the {label} page.")


@app.get("/")
@app.get("/api")
async def root():
    return {"ok": True, "service": "swgoh-tracker-sync", "version": APP_VERSION}


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"ok": True, "version": APP_VERSION, "provider": "swgoh.gg-public"}


@app.post("/sync")
@app.post("/api/sync")
async def sync(req: SyncRequest):
    code = clean_code(req.allyCode)
    profile_url = f"{SWGOH_GG_BASE}/p/{code}/"
    roster_url = f"{SWGOH_GG_BASE}/p/{code}/characters/"
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:
            profile_html, roster_html = await asyncio.gather(
                fetch_page(client, profile_url, "profile"),
                fetch_page(client, roster_url, "character roster"),
            )
    except HTTPException:
        raise
    except Exception:
        # Never send backend tracebacks or upstream HTML to the browser.
        raise HTTPException(status_code=502, detail="The public profile sync failed unexpectedly. Please try again later.")

    profile = parse_profile(profile_html, code)
    roster = parse_roster(roster_html)
    if not profile.get("gp") and not roster:
        raise HTTPException(
            status_code=502,
            detail="SWGOH.GG pages loaded, but no GP or roster data could be read. The site may have changed its page layout.",
        )

    if roster and not profile.get("rosterCount"):
        profile["rosterCount"] = len(roster)

    return {
        "allyCode": code,
        "profile": profile,
        "roster": roster,
        "crystals": None,
        "source": "swgoh.gg-public",
        "inventory": None,
        "limitations": ["Public profile data only; private inventory and unequipped materials are not available."],
    }
