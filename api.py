import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

from planning_generator import generate_planning

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

app = FastAPI(title="PlanningMD API")


@app.get("/generate")
def generate(access_token: str = Query(..., description="API access token")):
    if not ACCESS_TOKEN or access_token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid access token")

    generate_planning()

    return {"status": "ok"}
