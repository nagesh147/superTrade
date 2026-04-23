from __future__ import annotations

from fastapi import APIRouter, Depends, Request

router = APIRouter(prefix="/directional", tags=["directional"])


@router.get("/status")
def directional_status() -> dict:
    return {"status": "directional stack loaded"}


@router.get("/note")
def directional_note() -> dict:
    return {
        "message": "Wire this router to the live orchestrator once exchange adapters and persistence are connected.",
    }
