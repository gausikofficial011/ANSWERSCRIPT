import asyncio
import httpx
import uuid
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_live_workflow():
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Login
        print("1. Logging in as teacher...")
        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "teacher@amaes.edu",
            "password": "Teacher@1234"
        })
        if login_res.status_code != 200:
            print(f"[ERR] Login failed: {login_res.status_code} {login_res.text}")
            return
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[OK] Authenticated successfully!")

        # 2. Upload Alice's Answer Sheet
        exam_id = "77777777-7777-7777-7777-777777777777"
        student_id = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
        pdf_path = Path("uploads/alice_cs202_answer_sheet.pdf")
        
        print(f"2. Uploading {pdf_path.name} for Exam {exam_id}...")
        with open(pdf_path, "rb") as f:
            files = {"files": (pdf_path.name, f, "application/pdf")}
            data = {"exam_id": exam_id, "student_id": student_id}
            upload_res = await client.post(f"{BASE_URL}/answer-sheets/upload", data=data, files=files, headers=headers)

        if upload_res.status_code != 201:
            print(f"[ERR] Upload failed: {upload_res.status_code} {upload_res.text}")
            return

        sheets = upload_res.json()
        sheet = sheets[0]
        sheet_id = sheet["id"]
        print(f"[OK] Uploaded answer sheet ID: {sheet_id}")
        print(f"     Initial Status: {sheet.get('processing_status')}")

        # 3. Poll processing status
        print("3. Polling for OCR and Evaluation completion...")
        for attempt in range(40):
            await asyncio.sleep(2)
            res = await client.get(f"{BASE_URL}/answer-sheets/{sheet_id}", headers=headers)
            current_sheet = res.json()
            status = current_sheet.get("processing_status")
            print(f"   [{attempt+1}] Status: {status}")
            if status in ("COMPLETED", "EVALUATED"):
                print("[OK] Processing reached terminal completed state!")
                break
            elif status == "FAILED":
                print("[ERR] Answer sheet processing failed!")
                break

        # 4. Check OCR results
        ocr_res = await client.get(f"{BASE_URL}/ocr/answer-sheets/{sheet_id}", headers=headers)
        if ocr_res.status_code == 200:
            ocr_data = ocr_res.json()
            print("\n4. OCR Extraction Summary:")
            for page in ocr_data:
                print(f"   Page {page.get('page_number')}: Confidence {page.get('average_confidence'):.2f}")
                text_preview = page.get('extracted_text', '')[:200].replace('\n', ' ')
                print(f"   Extracted preview: {text_preview}...")
        else:
            print(f"[INFO] OCR get returned {ocr_res.status_code}: {ocr_res.text}")

        # 5. Check Question Mappings
        map_res = await client.get(f"{BASE_URL}/question-mappings/answer-sheet/{sheet_id}", headers=headers)
        if map_res.status_code == 200:
            mappings = map_res.json()
            print(f"\n5. Question Mappings ({len(mappings)} mapped):")
            for m in mappings:
                print(f"   Question ID: {m.get('question_id')}, Answer Preview: {m.get('extracted_text', '')[:100]}...")
        else:
            print(f"[INFO] Question mapping returned {map_res.status_code}")

        # 6. Check Evaluations
        eval_res = await client.get(f"{BASE_URL}/evaluations/answer-sheet/{sheet_id}", headers=headers)
        if eval_res.status_code == 200:
            evals = eval_res.json()
            print(f"\n6. AI Evaluations ({len(evals)} evaluations):")
            for ev in evals:
                print(f"   Evaluation ID: {ev.get('id')}")
                print(f"   Suggested Score: {ev.get('suggested_score')} / {ev.get('max_score')}")
                print(f"   Final Score: {ev.get('final_score')}")
                print(f"   Feedback: {ev.get('feedback')}")
        else:
            print(f"[INFO] Evaluations returned {eval_res.status_code}")

if __name__ == "__main__":
    asyncio.run(test_live_workflow())
