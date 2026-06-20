"""
api/v1/router.py — Main API v1 Router Aggregator
"""

from fastapi import APIRouter

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.subjects import router as subjects_router
from app.api.v1.routers.students import router as students_router
from app.api.v1.routers.exams import router as exams_router
from app.api.v1.routers.questions import router as questions_router
from app.api.v1.routers.model_answers import router as model_answers_router
from app.api.v1.routers.rubrics import router as rubrics_router
from app.api.v1.routers.answer_sheets import router as answer_sheets_router
from app.api.v1.routers.ocr import router as ocr_router
from app.api.v1.routers.question_mappings import router as question_mappings_router
from app.api.v1.routers.evaluations import router as evaluations_router
from app.api.v1.routers.plagiarism import router as plagiarism_router

api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth_router)
api_router.include_router(subjects_router)
api_router.include_router(students_router)
api_router.include_router(exams_router)
api_router.include_router(questions_router)
api_router.include_router(model_answers_router)
api_router.include_router(rubrics_router)
api_router.include_router(answer_sheets_router)
api_router.include_router(ocr_router)
api_router.include_router(question_mappings_router)
api_router.include_router(evaluations_router)
api_router.include_router(plagiarism_router)
