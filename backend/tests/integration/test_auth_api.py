"""
tests/integration/test_auth_api.py — Integration Tests for Auth API Endpoints
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.dependencies.auth import get_current_user
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.role_model import RoleModel
from app.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel
from app.infrastructure.auth.password_service import PasswordService
from app.infrastructure.auth.jwt_service import JWTService
from app.domain.entities.user import User

# Setup a transient FastAPI app for endpoint routing integration tests
app = FastAPI()
app.include_router(auth_router)

mock_db = MagicMock(spec=AsyncSession)


def get_mock_db():
    yield mock_db


app.dependency_overrides[get_db_session] = get_mock_db
client = TestClient(app)



async def mock_execute(query, *args, **kwargs):
    import uuid
    model_class = None
    if hasattr(query, "column_descriptions") and len(query.column_descriptions) > 0:
        model_class = query.column_descriptions[0].get("entity")

    entity_id = None
    if hasattr(query, "compile"):
        try:
            params = query.compile().params
            for k, val in params.items():
                if k.startswith("id") and isinstance(val, uuid.UUID):
                    entity_id = val
                    break
        except Exception:
            pass

    if model_class and entity_id:
        model = await mock_db.get(model_class, entity_id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = model
        result.scalars.return_value.first.return_value = model
        result.scalar_one.return_value = 1
        result.scalar.return_value = 1
        result.scalars.return_value.all.return_value = [model] if model else []
        return result

    return mock_db.execute.return_value


async def mock_merge(model, *args, **kwargs):
    if not model:
        return model
    if hasattr(model, "id") and hasattr(model, "__class__"):
        try:
            existing = await mock_db.get(model.__class__, model.id)
            if existing:
                for col in model.__table__.columns:
                    val = getattr(model, col.name, None)
                    if val is not None:
                        setattr(existing, col.name, val)
                return existing
        except Exception:
            pass
    return model


@pytest.fixture(autouse=True)
def reset_mocks():
    mock_db.reset_mock()
    mock_db.merge = AsyncMock(side_effect=mock_merge)
    # Reset method mocks
    mock_db.execute = AsyncMock(side_effect=mock_execute)
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.get = AsyncMock()


def test_login_endpoint_success():
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    plain_password = "SecurePassword123!"
    hashed_password = PasswordService.hash_password(plain_password)

    # 1. Mock DB RoleModel
    role_model = RoleModel(id=role_id, name="teacher")

    # 2. Mock DB UserModel
    user_model = UserModel(
        id=user_id,
        email="teacher@example.com",
        username="teacher1",
        hashed_password=hashed_password,
        full_name="John Doe",
        role_id=role_id,
        is_active=True,
        role=role_model
    )

    # Setup database mocks
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = user_model
    mock_db.execute.return_value = mock_execute_result

    # Return None for get() so audit log save falls back to session.add() path
    mock_db.get = AsyncMock(return_value=None)

    # Execute request
    response = client.post(
        "/auth/login",
        json={"email": "teacher@example.com", "password": plain_password}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "teacher1"
    assert data["role"] == "teacher"
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_endpoint_validation_error():
    # Invalid email pattern
    response = client.post(
        "/auth/login",
        json={"email": "notanemail", "password": "Pass"}
    )
    assert response.status_code == 422  # Pydantic validation error


def test_login_endpoint_invalid_credentials():
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute_result

    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "WrongPassword123!"}
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_refresh_token_endpoint_success():
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    
    # 1. Generate active refresh token
    refresh_token = JWTService.create_refresh_token(user_id)
    token_hash = JWTService.hash_token(refresh_token)

    # 2. Mock DB objects
    role_model = RoleModel(id=role_id, name="teacher")
    user_model = UserModel(
        id=user_id,
        email="teacher@example.com",
        username="teacher1",
        hashed_password="hash",
        full_name="John Doe",
        role_id=role_id,
        is_active=True,
        role=role_model
    )
    
    db_token = RefreshTokenModel(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        is_revoked=False
    )

    # Setup database query mock
    # get_by_id logic call
    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == UserModel:
            return user_model
        if model_class == RoleModel:
            return role_model
        return None

    mock_db.get = AsyncMock(side_effect=mock_get)

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = db_token
    mock_db.execute.return_value = mock_execute_result

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_get_me_endpoint():
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    
    # 1. Generate token
    token = JWTService.create_access_token(user_id, "teacher1", "teacher")
    
    # 2. Mock User
    user = User(
        id=user_id,
        email="teacher@example.com",
        username="teacher1",
        hashed_password="hash",
        full_name="John Doe",
        role_id=role_id,
        role="teacher",
        is_active=True,
        created_at=datetime.now()
    )

    # Override get_current_user dependency
    async def override_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_current_user

    # Execute request
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "teacher1"
    assert data["email"] == "teacher@example.com"
    assert data["role"] == "teacher"

    # Cleanup dependency overrides
    del app.dependency_overrides[get_current_user]
