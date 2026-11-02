"""
tests/integration/test_operational_hardening.py — Operational Hardening Integration Tests
"""

from __future__ import annotations

import asyncio
import io
import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.testclient import TestClient

from app.api.v1.dependencies.auth import get_current_user
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.core.constants import UserRole
from app.infrastructure.storage.clamav_malware_scanner import ClamAVMalwareScanner

# 1. ClamAV Abstraction Behavior Tests
@pytest.mark.asyncio
async def test_clamav_scanner_ok():
    scanner = ClamAVMalwareScanner()
    mock_reader = AsyncMock()
    mock_writer = AsyncMock()
    mock_reader.read = AsyncMock(return_value=b"stream: OK\n")
    
    with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
        res = await scanner.scan(b"clean data", "clean.pdf")
        assert res is True

@pytest.mark.asyncio
async def test_clamav_scanner_infected():
    scanner = ClamAVMalwareScanner()
    mock_reader = AsyncMock()
    mock_writer = AsyncMock()
    mock_reader.read = AsyncMock(return_value=b"stream: Eicar-Signature FOUND\n")
    
    with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
        res = await scanner.scan(b"infected data", "infected.pdf")
        assert res is False

@pytest.mark.asyncio
async def test_clamav_scanner_fail_closed():
    with patch("asyncio.open_connection", side_effect=ConnectionRefusedError("Conn refused")), \
         patch("app.infrastructure.storage.clamav_malware_scanner.get_settings") as mock_settings:
        
        mock_settings.return_value.clamav_fail_closed = True
        scanner = ClamAVMalwareScanner()
        with pytest.raises(RuntimeError) as exc:
            await scanner.scan(b"data", "test.pdf")
        assert "Virus scanning service is currently unavailable" in str(exc.value)

@pytest.mark.asyncio
async def test_clamav_scanner_fail_open():
    with patch("asyncio.open_connection", side_effect=ConnectionRefusedError("Conn refused")), \
         patch("app.infrastructure.storage.clamav_malware_scanner.get_settings") as mock_settings:
        
        mock_settings.return_value.clamav_fail_closed = False
        scanner = ClamAVMalwareScanner()
        res = await scanner.scan(b"data", "test.pdf")
        assert res is True

# 2. Secret Validation Lifespan Tests
@pytest.mark.asyncio
async def test_startup_secret_validation_production_default():
    from app.main import lifespan
    import app.main
    
    with patch.object(app.main.settings, "environment", "production"), \
         patch.object(app.main.settings, "jwt_secret_key", "dev_secret_key_change_me_in_production"):
        mock_app = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            async with lifespan(mock_app):
                pass
        assert "JWT_SECRET_KEY cannot be default in production mode" in str(exc.value)

@pytest.mark.asyncio
async def test_startup_secret_validation_production_short():
    from app.main import lifespan
    import app.main
    
    with patch.object(app.main.settings, "environment", "production"), \
         patch.object(app.main.settings, "jwt_secret_key", "short_key"):
        mock_app = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            async with lifespan(mock_app):
                pass
        assert "JWT_SECRET_KEY length must be at least 32 characters in production" in str(exc.value)

@pytest.mark.asyncio
async def test_startup_secret_validation_development_warn():
    from app.main import lifespan
    import app.main
    
    with patch.object(app.main.settings, "environment", "development"), \
         patch.object(app.main.settings, "jwt_secret_key", "short_key"), \
         patch("app.main.logger.warning") as mock_warn:
        mock_app = MagicMock()
        async with lifespan(mock_app):
            pass
        mock_warn.assert_called()

# 3. Trusted Host Middleware Tests
def test_trusted_host_protection():
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    
    dummy_app = FastAPI()
    dummy_app.add_middleware(TrustedHostMiddleware, allowed_hosts=["allowed.com", "*.allowed.com"])
    
    @dummy_app.get("/test")
    def dummy_route():
        return {"status": "ok"}
        
    dummy_client = TestClient(dummy_app)
    
    resp = dummy_client.get("/test", headers={"host": "allowed.com"})
    assert resp.status_code == 200
    
    resp = dummy_client.get("/test", headers={"host": "sub.allowed.com"})
    assert resp.status_code == 200
    
    resp = dummy_client.get("/test", headers={"host": "disallowed.com"})
    assert resp.status_code == 400

# 4. Rate Limiting Tests
def test_rate_limiting_upload_endpoint():
    from app.infrastructure.security.rate_limiter import upload_rate_limiter
    from app.config import get_settings
    
    settings = get_settings()
    original_limit = settings.rate_limit_upload_limit
    original_window = settings.rate_limit_upload_window
    
    settings.rate_limit_upload_limit = 2
    settings.rate_limit_upload_window = 5
    
    upload_rate_limiter._history.clear()
    
    try:
        from app.infrastructure.security.rate_limiter import upload_rate_limit_dependency
        
        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        
        import anyio
        async def run_dep():
            await upload_rate_limit_dependency(request=mock_request, current_user=mock_user)
            
        anyio.run(run_dep)
        anyio.run(run_dep)
        
        with pytest.raises(HTTPException) as exc:
            anyio.run(run_dep)
        assert exc.value.status_code == 429
        assert "Too many upload requests" in exc.value.detail
        
    finally:
        settings.rate_limit_upload_limit = original_limit
        settings.rate_limit_upload_window = original_window
        upload_rate_limiter._history.clear()

# 5. Event Loop Cleanup Tests
def test_task_loop_cleanup():
    from app.tasks.ocr_tasks import process_answer_sheet_ocr
    
    with patch("app.tasks.ocr_tasks.ProcessAnswerSheetOCRUseCase") as mock_use_case:
        mock_use_case.return_value.execute = AsyncMock(return_value=[])
        
        original_new_event_loop = asyncio.new_event_loop
        spy_loops = []
        
        def spy_new_event_loop():
            loop = original_new_event_loop()
            spy_loops.append(loop)
            return loop
            
        with patch("asyncio.new_event_loop", side_effect=spy_new_event_loop), \
             patch("asyncio.get_event_loop", side_effect=RuntimeError("no loop")), \
             patch("app.tasks.ocr_tasks.AsyncSessionLocal"), \
             patch("app.tasks.ocr_tasks.celery_app"):
            
            try:
                process_answer_sheet_ocr(str(uuid.uuid4()))
            except Exception:
                pass
                
        assert len(spy_loops) == 1
        assert spy_loops[0].is_closed() is True

# 6. Operational Logging Hooks Tests
@pytest.mark.asyncio
async def test_logging_hooks_publish_results():
    from app.application.use_cases.results.publish_exam_results_use_case import PublishExamResultsUseCase
    from app.application.use_cases.results.publish_exam_results_use_case import logger as publish_logger
    from app.domain.exceptions.domain_exception import EntityNotFoundException
    
    mock_final_repo = MagicMock()
    mock_sheet_repo = MagicMock()
    mock_exam_repo = MagicMock()
    mock_exam_repo.get_by_id = AsyncMock(return_value=None)
    mock_audit_repo = MagicMock()
    
    use_case = PublishExamResultsUseCase(
        final_result_repo=mock_final_repo,
        answer_sheet_repo=mock_sheet_repo,
        exam_repo=mock_exam_repo,
        audit_repo=mock_audit_repo
    )
    
    with patch.object(publish_logger, 'info') as mock_info, \
         patch.object(publish_logger, 'error') as mock_error:
        
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid.uuid4(), uuid.uuid4())
            
        assert any("Attempting to publish exam results" in call[0][0] for call in mock_info.call_args_list)
        assert any("Failed to publish exam results" in call[0][0] for call in mock_error.call_args_list)

@pytest.mark.asyncio
async def test_logging_hooks_review_plagiarism():
    from app.application.use_cases.plagiarism.review_plagiarism_use_case import ReviewPlagiarismUseCase
    from app.application.use_cases.plagiarism.review_plagiarism_use_case import logger as plagiarism_logger
    from app.domain.exceptions.domain_exception import EntityNotFoundException
    
    mock_plag_repo = MagicMock()
    mock_plag_repo.get_by_id = AsyncMock(return_value=None)
    mock_sheet_repo = MagicMock()
    mock_audit_repo = MagicMock()
    
    use_case = ReviewPlagiarismUseCase(
        plagiarism_repo=mock_plag_repo,
        answer_sheet_repo=mock_sheet_repo,
        audit_repo=mock_audit_repo
    )
    
    with patch.object(plagiarism_logger, 'info') as mock_info, \
         patch.object(plagiarism_logger, 'error') as mock_error:
        
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid.uuid4(), "CONFIRMED_PLAGIARISM", "notes", uuid.uuid4())
            
        assert any("Attempting to review plagiarism report" in call[0][0] for call in mock_info.call_args_list)
        assert any("Failed to review plagiarism report" in call[0][0] for call in mock_error.call_args_list)

def test_logging_hooks_csv_export():
    from app.api.v1.routers.result_exports import logger as export_logger
    from app.api.v1.routers.result_exports import router
    from app.api.v1.dependencies.auth import require_teacher
    
    dummy_app = FastAPI()
    dummy_app.include_router(router)
    
    async def override_user():
        return User(
            email="teacher@example.com",
            username="teacher1",
            hashed_password="hash",
            full_name="Teacher",
            role="teacher",
            id=uuid.uuid4()
        )
        
    dummy_app.dependency_overrides[require_teacher] = override_user
    dummy_client = TestClient(dummy_app)
    
    with patch.object(export_logger, 'info') as mock_info, \
         patch.object(export_logger, 'error') as mock_error:
        
        dummy_client.get(f"/results/exams/{uuid.uuid4()}/export/csv")
        
        assert any("Exporting exam results CSV attempt" in call[0][0] for call in mock_info.call_args_list)
        assert any("Exporting exam results CSV failed" in call[0][0] for call in mock_error.call_args_list)
