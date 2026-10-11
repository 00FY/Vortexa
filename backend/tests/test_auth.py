import uuid
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token, decode_access_token
from schemas.auth import LoginRequest

client = TestClient(app)


def test_hash_and_verify_real():
    h = hash_password("test")
    assert verify_password("test", h)
    assert not verify_password("wrong", h)


def test_jwt_create_decode_real():
    token = create_access_token({"sub": "u1"})
    payload = decode_access_token(token)
    assert payload and payload.get("sub") == "u1"


def test_login_sets_cookie_and_no_token_in_body():
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.email = "test@novapay.com"
    mock_user.id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    mock_user.hashed_password = hash_password("correct")
    mock_user.is_active = True
    mock_user.role = "employee"
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        resp = client.post("/api/auth/login", json={"email": "test@novapay.com", "password": "correct"})
        assert resp.status_code == 200
        assert "access_token" in resp.cookies
        body = resp.json()
        assert "access_token" not in body
    finally:
        app.dependency_overrides.clear()


def test_invalid_password_401():
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.email = "bad@novapay.com"
    mock_user.hashed_password = hash_password("real")
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        resp = client.post("/api/auth/login", json={"email": "bad@novapay.com", "password": "wrong"})
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_unknown_email_401():
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        resp = client.post("/api/auth/login", json={"email": "no@novapay.com", "password": "anything"})
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_me_authenticated_profile():
    test_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    token = create_access_token({"sub": str(test_id)})
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.id = test_id
    mock_user.email = "me@novapay.com"
    mock_user.role = "employee"
    mock_user.is_active = True
    mock_session.get.return_value = mock_user
    mock_session.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        resp = client.get("/api/auth/me", cookies={"access_token": token})
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@novapay.com"
    finally:
        app.dependency_overrides.clear()


def test_me_missing_cookie_401():
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_invalid_expired_jwt_401():
    resp = client.get("/api/auth/me", cookies={"access_token": "badtoken"})
    assert resp.status_code == 401


def test_inactive_user_401():
    test_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
    token = create_access_token({"sub": str(test_id)})
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.id = test_id
    mock_user.is_active = False
    mock_session.get.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        resp = client.get("/api/auth/me", cookies={"access_token": token})
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_logout_clears_cookie():
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    assert "access_token" not in resp.cookies or resp.cookies.get("access_token") == ""


def test_unauthorized_role_403():
    from core.dependencies import require_role

    mock_user = MagicMock()
    mock_user.id = uuid.UUID("33333333-3333-3333-3333-333333333333")
    mock_user.role = "employee"
    mock_user.is_active = True

    checker = require_role("admin")
    with pytest.raises(Exception):
        checker(current_user=mock_user)