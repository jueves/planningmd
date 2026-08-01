import os
from typing import Literal

from fastapi import FastAPI, HTTPException, Query

from planning_generator import generate_planning
from printer import print_pdf

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

app = FastAPI(title="PlanningMD API")


def _check_token(access_token: str) -> None:
    if not ACCESS_TOKEN or access_token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid access token")


@app.get("/generate")
def generate(
    access_token: str = Query(..., description="API access token"),
    columns: Literal["auto", "1", "2"] = Query(
        "2", description="Column layout: 'auto' (two columns only if content exceeds one page), '1' or '2'"
    ),
):
    _check_token(access_token)

    generate_planning(columns=columns)

    return {"status": "ok"}


@app.get("/print")
def print_planning(
    access_token: str = Query(..., description="API access token"),
    columns: Literal["auto", "1", "2"] = Query(
        "2", description="Column layout: 'auto' (two columns only if content exceeds one page), '1' or '2'"
    ),
):
    _check_token(access_token)

    path = generate_planning(columns=columns)

    try:
        print_pdf(path)
    except Exception as exc:
        print(f"Printing failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Printing failed: {exc}")

    return {"status": "ok", "printed": path}
