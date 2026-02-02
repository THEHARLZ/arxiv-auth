"""Minimal personal AI assistant endpoint."""

from typing import Optional, Callable, Dict, Any

from fastapi import APIRouter, Depends, HTTPException

from .domain import User


def create_assistant_router(auth_dependency: Callable) -> APIRouter:
    """
    Build an assistant router that enforces authentication.

    Parameters
    ----------
    auth_dependency : Callable
        Dependency that returns an authenticated :class:`User` or raises.
    """
    router = APIRouter()

    @router.post("/assistant")
    async def assistant(
        payload: Optional[Dict[str, Any]] = None,
        user: User = Depends(auth_dependency),
    ) -> Dict[str, str]:
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        message = ""
        if isinstance(payload, dict):
            message = payload.get("message", "") or ""
        reply = f"AI assistant reply: {message}" if message else "AI assistant ready."
        return {"reply": reply}

    return router
