import os, re, json
from typing import Any
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SWGOH Tracker v0.5.2 Sync")
SWGOH_GG_BASE = os.getenv("SWGOH_GG_BASE", "https://swgoh.gg").rstrip("/")

class SyncRequest(BaseModel):
    allyCode: str

def clean_code(value: str) -> str:
    code = re.sub(r"\D", "", value or "")
    if len(code) != 9:
        raise HTTPException(400, "Ally Code must be exactly 9 digits.")
    return code

def number(text: str | None) -> int | None:
    if not text: return None
    m = re.search(r"[\d,]+", text)
    return int(m.group(0).replace(",", "")) if m else None

def parse_profile(html: str, code: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    profile = {"allyCode": code}
    m = re.search(r"Galactic Power\s+([\d,]+)", text, re.I)
    if m: profile["gp"] = int(m.group(1).replace(",", ""))
    m = re.search(r"(\d+)\s+units", text, re.I)
    if m: profile["rosterCount"] = int(m.group(1))
    # SWGOH.GG's public profile is intentionally parsed conservatively.
    # The UI remains usable if a field changes; raw page parsing is isolated here.
    return profile

def parse_roster(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    units: list[dict[str, Any]] = []
    # Try structured attributes commonly used by SWGOH.GG cards/tables.
    for node in soup.select("[data-unit-id], [data-definition-id]"):
        name = node.get_text(" ", strip=True)
        unit_id = node.get("data-unit-id") or node.get("data-definition-id")
        if unit_id:
            units.append({"id": unit_id, "name": name})
    return units

@app.get("/health")
async def health():
    return {"ok": True, "version": "0.5.2", "provider": "swgoh.gg-public"}

@app.post("/sync")
async def sync(req: SyncRequest):
    code = clean_code(req.allyCode)
    url = f"{SWGOH_GG_BASE}/p/{code}/"
    headers = {"User-Agent": "SWGOH-Tracker/0.5.2 public-profile-sync"}
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text
    except Exception as exc:
        raise HTTPException(502, f"SWGOH.GG request failed: {exc}")

    profile = parse_profile(html, code)
    roster = parse_roster(html)
    return {
        "allyCode": code,
        "profile": profile,
        "roster": roster,
        "crystals": None,
        "source": "swgoh.gg-public",
        "inventory": None
    }
