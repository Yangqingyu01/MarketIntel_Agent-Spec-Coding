"""Authentication API routes for demo login."""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth.service import (
    AuthenticatedUser,
    create_demo_account,
    login_user,
    require_authenticated_user,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=80)
    full_name: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=6, max_length=128)


@router.post("/register")
async def register(payload: RegisterRequest) -> Dict:
    return create_demo_account(
        organization_name=payload.organization_name,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
    )


@router.post("/login")
async def login(payload: LoginRequest) -> Dict:
    return login_user(email=payload.email, password=payload.password)


@router.get("/me")
async def me(user: AuthenticatedUser = Depends(require_authenticated_user)) -> Dict:
    return {"user": user.to_dict()}
