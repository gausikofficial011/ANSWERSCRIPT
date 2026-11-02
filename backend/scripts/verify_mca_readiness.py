import os
from pathlib import Path
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        try:
            # Check overview stats endpoint
            res = await client.get("http://127.0.0.1:8000/api/v1/results/overview")
            print(f"[OK] GET /results/overview returned status: {res.status_code}")
            if res.status_code == 401:
                print("  (Authentication validation behaves as expected)")
        except Exception as e:
            print(f"[ERROR] API connection check failed: {e}")

def check_docs():
    required_docs = [
        "SYSTEM_ARCHITECTURE.md",
        "WORKFLOW_DOCUMENTATION.md",
        "DEPLOYMENT_GUIDE.md",
        "API_REFERENCE.md",
        "DATABASE_DOCUMENTATION.md",
        "AI_PIPELINE_DOCUMENTATION.md",
        "UNIT_TEST_SUMMARY.md",
        "INTEGRATION_TEST_SUMMARY.md",
        "UAT_REPORT.md",
        "PERFORMANCE_REPORT.md",
        "MCA_PROJECT_DOCUMENTATION.md",
        "VIVA_PREPARATION.md",
        "FINAL_PROJECT_AUDIT.md",
        "FINAL_MCA_READINESS_REPORT.md",
        "FINAL_UI_REVIEW.md",
        "FINAL_DOCUMENTATION_INDEX.md",
        "FINAL_DEPLOYMENT_CHECKLIST.md"
    ]
    docs_dir = Path("docs")
    errors = 0
    for doc in required_docs:
        p = docs_dir / doc
        if p.exists():
            print(f"[OK] Document exists: {doc} ({p.stat().st_size} bytes)")
        else:
            print(f"[ERROR] Missing document: {doc}")
            errors += 1
    if errors == 0:
        print("[OK] All 17 required documents are present.")
    else:
        print(f"[ERROR] {errors} document(s) are missing.")

if __name__ == "__main__":
    print("--- STARTING MCA FINAL VERIFICATION ---")
    check_docs()
    asyncio.run(test_api())
    print("--- VERIFICATION COMPLETED ---")
