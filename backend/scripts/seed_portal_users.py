"""
backend/scripts/seed_portal_users.py

Seed dedicated institutional accounts for each of the 10 role-specific portals.
"""

import asyncio
import uuid
from sqlalchemy import select
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.auth.password_service import PasswordService

PORTAL_USERS = [
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000001"),
        "email": "superadmin@amaes.edu",
        "username": "superadmin",
        "full_name": "Platform Administrator",
        "password": "Admin@1234",
        "role_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),  # admin
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000002"),
        "email": "academic_admin@amaes.edu",
        "username": "academic_admin",
        "full_name": "Dr. Smith (Dean Academics)",
        "password": "Admin@1234",
        "role_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),  # admin
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000003"),
        "email": "teacher@amaes.edu",
        "username": "teacher",
        "full_name": "Prof. Kumar (Exam Creator)",
        "password": "Teacher@1234",
        "role_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),  # teacher
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000004"),
        "email": "ocr@amaes.edu",
        "username": "ocr_reviewer",
        "full_name": "Prof. Kumar (OCR Specialist)",
        "password": "Teacher@1234",
        "role_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),  # teacher
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000005"),
        "email": "ai_eval@amaes.edu",
        "username": "ai_eval_lead",
        "full_name": "Dr. Jane Smith (AI Diagnostics)",
        "password": "Teacher@1234",
        "role_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),  # teacher
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000006"),
        "email": "evaluator@amaes.edu",
        "username": "evaluator_moderator",
        "full_name": "Prof. Sharma (Moderator)",
        "password": "Teacher@1234",
        "role_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),  # teacher
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000007"),
        "email": "integrity@amaes.edu",
        "username": "integrity_officer",
        "full_name": "Dr. Vance (Integrity Board)",
        "password": "Admin@1234",
        "role_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),  # admin
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000008"),
        "email": "student@amaes.edu",
        "username": "arjun_kumar",
        "full_name": "Arjun Kumar (Roll: CS204015)",
        "password": "Student@1234",
        "role_id": uuid.UUID("33333333-1111-1111-1111-111111111111"),  # student
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000009"),
        "email": "analytics@amaes.edu",
        "username": "analytics_lead",
        "full_name": "Quality Assurance & Analytics Lead",
        "password": "Admin@1234",
        "role_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),  # admin
    },
    {
        "id": uuid.UUID("10000000-0000-0000-0000-000000000010"),
        "email": "research@amaes.edu",
        "username": "research_scientist",
        "full_name": "Dr. AI Researcher (ML Lab)",
        "password": "Admin@1234",
        "role_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),  # admin
    },
]

async def seed():
    print("Seeding dedicated institutional portal accounts...")
    async for db in get_db_session():
        for item in PORTAL_USERS:
            res = await db.execute(select(UserModel).where(UserModel.email == item["email"]))
            existing = res.scalar_one_or_none()
            hashed_pwd = PasswordService.hash_password(item["password"])
            if existing:
                existing.full_name = item["full_name"]
                existing.hashed_password = hashed_pwd
                existing.role_id = item["role_id"]
                existing.is_active = True
                existing.is_verified = True
                print(f"Updated existing user: {item['email']}")
            else:
                user = UserModel(
                    id=item["id"],
                    email=item["email"],
                    username=item["username"],
                    full_name=item["full_name"],
                    hashed_password=hashed_pwd,
                    role_id=item["role_id"],
                    is_active=True,
                    is_verified=True,
                )
                db.add(user)
                print(f"Created new user: {item['email']}")
        await db.commit()
        print("All 10 portal accounts seeded successfully!")
        break

if __name__ == "__main__":
    asyncio.run(seed())
