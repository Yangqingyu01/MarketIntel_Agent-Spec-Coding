"""Minimal organization + user auth services for demo login."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import config


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    user_id: str
    email: str
    full_name: str
    organization_id: str
    organization_name: str
    role: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "organization_id": self.organization_id,
            "organization_name": self.organization_name,
            "role": self.role,
        }


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(config.sqlite_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS organizations (
            organization_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS memberships (
            user_id TEXT NOT NULL,
            organization_id TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (user_id, organization_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
        )
        """
    )
    connection.commit()
    return connection


def initialize_auth_storage() -> None:
    _connect().close()


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    chars = []
    last_dash = False
    for char in lowered:
        if char.isalnum():
            chars.append(char)
            last_dash = False
        elif not last_dash:
            chars.append("-")
            last_dash = True
    slug = "".join(chars).strip("-")
    return slug or "organization"


def _password_hash(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return "{salt}${digest}".format(
        salt=salt.hex(),
        digest=digest.hex(),
    )


def _verify_password(password: str, encoded: str) -> bool:
    try:
        salt_hex, digest_hex = encoded.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(actual, expected)


def _encode_token(payload: Dict[str, Any]) -> str:
    payload_bytes = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload_segment = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=")
    signature = hmac.new(
        config.auth_secret_key.encode("utf-8"),
        payload_segment,
        hashlib.sha256,
    ).digest()
    signature_segment = base64.urlsafe_b64encode(signature).rstrip(b"=")
    return b".".join([payload_segment, signature_segment]).decode("utf-8")


def _decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload_segment, signature_segment = token.split(".", 1)
    except ValueError:
        return None

    expected_signature = hmac.new(
        config.auth_secret_key.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    actual_signature = base64.urlsafe_b64decode(signature_segment + "=" * (-len(signature_segment) % 4))
    if not hmac.compare_digest(expected_signature, actual_signature):
        return None

    try:
        payload_bytes = base64.urlsafe_b64decode(payload_segment + "=" * (-len(payload_segment) % 4))
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

    exp = int(payload.get("exp", 0))
    if exp <= int(_utc_now().timestamp()):
        return None
    return payload


def _build_auth_user(row: sqlite3.Row) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=str(row["user_id"]),
        email=str(row["email"]),
        full_name=str(row["full_name"]),
        organization_id=str(row["organization_id"]),
        organization_name=str(row["organization_name"]),
        role=str(row["role"]),
    )


def _fetch_user_context_by_id(connection: sqlite3.Connection, user_id: str) -> Optional[AuthenticatedUser]:
    row = connection.execute(
        """
        SELECT
            users.user_id,
            users.email,
            users.full_name,
            organizations.organization_id,
            organizations.name AS organization_name,
            memberships.role
        FROM users
        JOIN memberships ON memberships.user_id = users.user_id
        JOIN organizations ON organizations.organization_id = memberships.organization_id
        WHERE users.user_id = ? AND users.is_active = 1
        ORDER BY memberships.created_at ASC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    return _build_auth_user(row) if row else None


def _issue_token_for_user(user: AuthenticatedUser) -> str:
    issued_at = _utc_now()
    expires_at = issued_at + timedelta(hours=config.auth_token_ttl_hours)
    return _encode_token(
        {
            "sub": user.user_id,
            "org": user.organization_id,
            "role": user.role,
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
    )


def create_demo_account(
    organization_name: str,
    full_name: str,
    email: str,
    password: str,
) -> Dict[str, Any]:
    initialize_auth_storage()
    normalized_email = email.strip().lower()
    if not normalized_email or "@" not in normalized_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
    if len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short")

    connection = _connect()
    existing = connection.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (normalized_email,),
    ).fetchone()
    if existing:
        connection.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    organization_id = "org_" + secrets.token_hex(8)
    user_id = "user_" + secrets.token_hex(8)
    slug_base = _slugify(organization_name)
    slug = slug_base
    suffix = 1
    while connection.execute(
        "SELECT 1 FROM organizations WHERE slug = ?",
        (slug,),
    ).fetchone():
        suffix += 1
        slug = "{base}-{suffix}".format(base=slug_base, suffix=suffix)

    created_at = _utc_now().isoformat()
    connection.execute(
        "INSERT INTO organizations (organization_id, name, slug, created_at) VALUES (?, ?, ?, ?)",
        (organization_id, organization_name.strip(), slug, created_at),
    )
    connection.execute(
        "INSERT INTO users (user_id, email, full_name, password_hash, created_at, is_active) VALUES (?, ?, ?, ?, ?, 1)",
        (
            user_id,
            normalized_email,
            full_name.strip() or normalized_email.split("@", 1)[0],
            _password_hash(password),
            created_at,
        ),
    )
    connection.execute(
        "INSERT INTO memberships (user_id, organization_id, role, created_at) VALUES (?, ?, ?, ?)",
        (user_id, organization_id, "admin", created_at),
    )
    connection.commit()
    user = _fetch_user_context_by_id(connection, user_id)
    connection.close()
    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Account setup failed")
    return {
        "access_token": _issue_token_for_user(user),
        "token_type": "bearer",
        "user": user.to_dict(),
    }


def login_user(email: str, password: str) -> Dict[str, Any]:
    initialize_auth_storage()
    connection = _connect()
    row = connection.execute(
        "SELECT user_id, password_hash, is_active FROM users WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()
    if not row or int(row["is_active"]) != 1 or not _verify_password(password, str(row["password_hash"])):
        connection.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    user = _fetch_user_context_by_id(connection, str(row["user_id"]))
    connection.close()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Membership not found")
    return {
        "access_token": _issue_token_for_user(user),
        "token_type": "bearer",
        "user": user.to_dict(),
    }


def get_user_from_token(token: str) -> AuthenticatedUser:
    payload = _decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    connection = _connect()
    user = _fetch_user_context_by_id(connection, str(payload.get("sub", "")))
    connection.close()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_authenticated_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return get_user_from_token(credentials.credentials)

