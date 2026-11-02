import asyncio
import httpx

async def inspect():
    async with httpx.AsyncClient() as client:
        login = await client.post('http://127.0.0.1:8000/api/v1/auth/login', json={'email':'teacher@amaes.edu','password':'Teacher@1234'})
        token = login.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        sheet_id = '2c3ff932-537a-4b5c-97d7-8a5519b5ee38'
        
        ocr_res = await client.get(f'http://127.0.0.1:8000/api/v1/ocr/{sheet_id}/results', headers=headers)
        print('=== OCR RESULTS ===')
        for r in ocr_res.json():
            print(f"Page {r['page_number']}: Confidence {r['average_confidence']:.2f}")
            print('Extracted Text:\n', r['extracted_text'])

        map_res = await client.get(f'http://127.0.0.1:8000/api/v1/ocr/{sheet_id}/mappings', headers=headers)
        print('\n=== QUESTION MAPPINGS ===')
        for m in map_res.json():
            print(f"Question ID: {m.get('question_id')}")
            print(f"Confidence: {m.get('confidence')}")
            print(f"Text:\n{m.get('extracted_text')}")

        eval_res = await client.get(f'http://127.0.0.1:8000/api/v1/evaluations/answer-sheets/{sheet_id}', headers=headers)
        print('\n=== EVALUATION DETAILS ===')
        for ev in eval_res.json():
            print(f"Evaluation ID: {ev.get('id')}")
            print(f"Suggested Score: {ev.get('suggested_score')} / {ev.get('max_score')}")
            print(f"Final Score: {ev.get('final_score')}")
            print(f"Requires Review: {ev.get('requires_review')}")
            print(f"Feedback: {ev.get('feedback')}")

if __name__ == '__main__':
    asyncio.run(inspect())
