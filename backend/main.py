import os, re
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app=FastAPI(title="SWGOH Tracker v0.5 Sync")
COMLINK_URL=os.getenv("COMLINK_URL","http://localhost:8080").rstrip("/")
API_KEY=os.getenv("API_KEY","")

class SyncRequest(BaseModel):
    allyCode:str

@app.get("/health")
def health():
    return {"ok":True,"version":"0.5"}

@app.post("/sync")
async def sync(req:SyncRequest):
    code=re.sub(r"\D","",req.allyCode)
    if len(code)!=9:
        raise HTTPException(400,"Ally Code must be exactly 9 digits.")
    headers={"Content-Type":"application/json"}
    if API_KEY: headers["Authorization"]=f"Bearer {API_KEY}"
    # Comlink deployments vary in their route wrapper. Keep the endpoint isolated here
    # so the PWA never needs to know the Comlink implementation details.
    payload={"allyCode":int(code)}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r=await client.post(f"{COMLINK_URL}/player",json=payload,headers=headers)
            r.raise_for_status()
            data=r.json()
    except Exception as e:
        raise HTTPException(502,f"Comlink request failed: {e}")
    profile=data.get("playerProfile",data.get("profile",{}))
    returned=str(profile.get("allyCode",data.get("allyCode",code))).replace("-","")
    if returned and returned!=code:
        raise HTTPException(502,"Returned account does not match requested Ally Code.")
    roster=data.get("rosterUnit",data.get("roster",[]))
    return {"allyCode":code,"profile":profile,"roster":roster,"crystals":data.get("crystals")}
