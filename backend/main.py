import os,re
import httpx
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,field_validator
app=FastAPI(title='SWGOH Tracker v0.5 Sync API',version='0.5')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('ALLOW_ORIGINS','*').split(','),allow_credentials=False,allow_methods=['POST','GET'],allow_headers=['*'])
COMLINK_URL=os.getenv('COMLINK_URL','http://localhost:3000').rstrip('/')
COMLINK_ACCESS=os.getenv('COMLINK_ACCESS_KEY')
COMLINK_SECRET=os.getenv('COMLINK_SECRET_KEY')
class SyncRequest(BaseModel):
    allyCode:str
    @field_validator('allyCode')
    @classmethod
    def valid_code(cls,v):
        n=re.sub(r'\D','',v)
        if len(n)!=9: raise ValueError('Ally Code must contain exactly 9 digits')
        return n
@app.get('/api/health')
def health(): return {'ok':True,'comlink':COMLINK_URL}
@app.post('/api/sync')
async def sync(req:SyncRequest):
    headers={'Content-Type':'application/json'}
    # HMAC headers are intentionally delegated to the official comlink client in production.
    # If your Comlink instance has no HMAC, this direct request is sufficient.
    payload={'payload':{'allyCode':req.allyCode},'enums':False}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r=await client.post(COMLINK_URL+'/player',json=payload,headers=headers)
            r.raise_for_status(); data=r.json()
    except Exception as e:
        raise HTTPException(502,f'Comlink sync failed: {e}')
    if str(data.get('allyCode','')).replace('-','')!=req.allyCode:
        raise HTTPException(502,'Comlink returned a different Ally Code')
    roster=data.get('rosterUnit',[])
    profile={'name':data.get('name','Player'),'allyCode':data.get('allyCode'),'playerId':data.get('playerId'),'gp':data.get('galacticPower') or data.get('gp'),'level':data.get('level'),'guildId':data.get('guildId'),'guildName':data.get('guildName')}
    return {'allyCode':req.allyCode,'profile':profile,'roster':roster}
