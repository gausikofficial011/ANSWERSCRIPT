"""
create_admin_user.py — One-time script to seed an admin user into the DB.
Run with: python create_admin_user.py
"""

import asyncio
import uuid
import sys
import os

# Ensure the app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

import bcrypt

# ── Config ────────────────────────────────────────────────────────────────────
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/answer_evaluation"

EMAIL    = "admin@eval.com"
USERNAME = "admin"
PASSWORD = "Admin@1234"
FULLNAME = "System Administrator"

# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Ensure 'admin' role exists (or pick first available role)
        result = await session.execute(
            text("SELECT id FROM roles WHERE name = 'admin' LIMIT 1")
        )
        row = result.fetchone()

        if row:
            role_id = row[0]
            print(f"[OK] Found existing 'admin' role: {role_id}")
        else:
            # Try any role
            result = await session.execute(text("SELECT id, name FROM roles LIMIT 5"))
            rows = result.fetchall()
            if not rows:
                print("[ERR] No roles found in DB. Make sure the DB is initialised first.")
                return
            role_id = rows[0][0]
            print(f"[INFO] No 'admin' role found, using role '{rows[0][1]}': {role_id}")

        # 2. Check if user already exists
        result = await session.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": EMAIL}
        )
        existing = result.fetchone()
        if existing:
            print(f"[OK] User '{EMAIL}' already exists -- no action taken.")
            return

        # 3. Insert the user
        user_id = uuid.uuid4()
        hashed = hash_password(PASSWORD)

        await session.execute(
            text("""
                INSERT INTO users (id, email, username, hashed_password, full_name, role_id, is_active, is_verified)
                VALUES (:id, :email, :username, :hashed_password, :full_name, :role_id, TRUE, TRUE)
            """),
            {
                "id": str(user_id),
                "email": EMAIL,
                "username": USERNAME,
                "hashed_password": hashed,
                "full_name": FULLNAME,
                "role_id": str(role_id),
            },
        )
        await session.commit()
        print(f"[OK] Admin user created successfully!")
        print(f"   Email    : {EMAIL}")
        print(f"   Username : {USERNAME}")
        print(f"   Password : {PASSWORD}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
#