import asyncio
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def complete_workflow():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Login as teacher
        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "teacher@amaes.edu",
            "password": "Teacher@1234"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        exam_id = "77777777-7777-7777-7777-777777777777"
        sheet_id = "2c3ff932-537a-4b5c-97d7-8a5519b5ee38"
        eval_id = "8934961d-290d-4a64-ad1d-bca0b699d87f"

        # 1. Teacher Verification & Score Override
        print("1. Submitting Teacher Review and Score Override...")
        verify_payload = {
            "teacher_score": 9.5,
            "teacher_feedback": "Excellent and concise explanation. Accurate definitions of LIFO and FIFO.",
            "reason": "Accurate definitions and full concept coverage justified a slight upward adjustment."
        }
        v_res = await client.post(f"{BASE_URL}/evaluations/{eval_id}/verify", json=verify_payload, headers=headers)
        print(f"   Verify HTTP status: {v_res.status_code}")
        if v_res.status_code == 200:
            v_data = v_res.json()
            print(f"[OK] Evaluation verified!")
            print(f"     AI Score: {v_data.get('ai_score')}")
            print(f"     Teacher Score: {v_data.get('teacher_score')}")
            print(f"     Final Score: {v_data.get('final_score')}")
            print(f"     Is Verified: {v_data.get('is_verified')}")
        else:
            print(f"[ERR] Verify failed: {v_res.text}")

        # 2. Calculate Final Results for the Exam
        print("\n2. Calculating Final Results for Exam...")
        calc_res = await client.post(f"{BASE_URL}/results/exams/{exam_id}/calculate", headers=headers)
        print(f"   Calculate HTTP status: {calc_res.status_code}")
        if calc_res.status_code == 200:
            calc_data = calc_res.json()
            print(f"[OK] Final results calculated: {calc_data}")
        else:
            print(f"[INFO] Calculate response: {calc_res.text}")

        # 3. Publish Exam Results
        print("\n3. Publishing Exam Results...")
        pub_res = await client.post(f"{BASE_URL}/results/exams/{exam_id}/publish", headers=headers)
        print(f"   Publish HTTP status: {pub_res.status_code}")
        if pub_res.status_code == 200:
            print(f"[OK] Exam results published successfully!")
        else:
            print(f"[INFO] Publish response: {pub_res.text}")

        # 4. Fetch Exam Results Summary
        print("\n4. Fetching Published Exam Results...")
        results_res = await client.get(f"{BASE_URL}/results/exams/{exam_id}", headers=headers)
        print(f"   Results HTTP status: {results_res.status_code}")
        if results_res.status_code == 200:
            res_data = results_res.json()
            print(f"[OK] Exam Results Data: {res_data}")

        # 5. Fetch Student Transcript
        student_id = res_data['items'][0]['student_id'] if (res_data and res_data.get('items')) else "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
        print(f"\n5. Fetching Transcript for Student {student_id}...")
        trans_res = await client.get(f"{BASE_URL}/results/students/{student_id}", headers=headers)
        print(f"   Transcript HTTP status: {trans_res.status_code}")
        if trans_res.status_code == 200:
            print(f"[OK] Student Transcript: {trans_res.json()}")
        else:
            print(f"[ERR] Transcript error: {trans_res.text}")

if __name__ == "__main__":
    asyncio.run(complete_workflow())
