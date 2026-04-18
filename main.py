from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
import re

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

def sanitize_mongo_uri(uri: str) -> str:
    pattern = re.compile(r"^(mongodb(?:\+srv)?://)([^:/?#]+):(.+)@(.+)$")
    match = pattern.match(uri)
    if not match:
        return uri
    prefix, username, password, rest = match.groups()
    safe_username = quote_plus(username)
    safe_password = quote_plus(password)
    return f"{prefix}{safe_username}:{safe_password}@{rest}"

mongo_uri = sanitize_mongo_uri(MONGO_URI) if MONGO_URI else None
client = AsyncIOMotorClient(mongo_uri)
db = client["euron"]
euron_data = db["euron_coll"]

app = FastAPI()

class eurondata(BaseModel):
    name: str
    phone: int
    city: str
    course: str
    
@app.post("/euron/insert")    
async def euron_data_insert_helper(data:eurondata):
    result  = await euron_data.insert_one(data.dict())
    return str(result.inserted_id)

def euron_helper(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@app.get("/euron/getdata")
async def get_euron_data():
    iterms = []
    cursor = euron_data.find({})
    async for document in cursor:
        iterms.append(euron_helper(document))
    return iterms

@app.get("/euron/showdata")
async def show_euron_data():
    iterms = []
    cursor = euron_data.find({})
    async for document in cursor:
        iterms.append(euron_helper(document))
    return iterms
    