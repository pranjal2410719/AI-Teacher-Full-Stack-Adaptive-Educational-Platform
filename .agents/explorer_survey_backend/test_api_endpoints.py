import requests
import json
import io

BASE_URL = "http://localhost:8000"

results = {}

def run_test(name, fn):
    print(f"Testing: {name}")
    try:
        res = fn()
        results[name] = {"status": "SUCCESS", "data": res}
        print(f"  -> SUCCESS")
    except Exception as e:
        results[name] = {"status": "FAILED", "error": str(e)}
        print(f"  -> FAILED: {e}")

# 1. Health
def test_health():
    r = requests.get(f"{BASE_URL}/api/v1/health")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("GET /api/v1/health", test_health)

# 2. Topic Ingestion
topic_id = None
def test_topic_ingest():
    global topic_id
    payload = {"topic": "Limits, Continuity & Epsilon-Delta Definition", "subject_category": "Mathematics"}
    r = requests.post(f"{BASE_URL}/api/v1/materials/topic", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()
    topic_id = data["topic_id"]
    return data
run_test("POST /api/v1/materials/topic", test_topic_ingest)

# 3. Document Upload
doc_id = None
def test_doc_upload():
    global doc_id
    file_content = b"# Calculus Limits\nA limit is the value that a function approaches as the input approaches some value.\nFormal epsilon-delta definition controls error."
    files = {"file": ("calculus_test.md", io.BytesIO(file_content), "text/markdown")}
    r = requests.post(f"{BASE_URL}/api/v1/materials/upload", files=files)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()
    doc_id = data["document_id"]
    return data
run_test("POST /api/v1/materials/upload", test_doc_upload)

# 4. Document Metadata
def test_doc_meta():
    r = requests.get(f"{BASE_URL}/api/v1/materials/{doc_id}")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("GET /api/v1/materials/{doc_id}", test_doc_meta)

# 5. List Materials
def test_list_materials():
    r = requests.get(f"{BASE_URL}/api/v1/materials")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return {"count": len(r.json()), "sample": r.json()[:2]}
run_test("GET /api/v1/materials", test_list_materials)

# 6. RAG Query
def test_rag_query():
    payload = {"document_id": doc_id, "query": "epsilon delta limit", "top_k": 3}
    r = requests.post(f"{BASE_URL}/api/v1/materials/query", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("POST /api/v1/materials/query", test_rag_query)

# 7. Lesson Plan Creation
plan_id = None
def test_lesson_plan():
    global plan_id
    payload = {
        "learner_profile": {
            "student_id": "stu_test_001",
            "level": "intermediate",
            "language": "en",
            "time_budget_min": 15
        },
        "topic_id": topic_id
    }
    r = requests.post(f"{BASE_URL}/api/v1/lessons/plan", json=payload)
    assert r.status_code in [200, 201], f"Status {r.status_code}: {r.text}"
    data = r.json()
    plan_id = data["plan_id"]
    return data
run_test("POST /api/v1/lessons/plan", test_lesson_plan)

# 8. Get Lesson Plan via /api/v1/lessons/{plan_id}
def test_get_plan_backend():
    r = requests.get(f"{BASE_URL}/api/v1/lessons/{plan_id}")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("GET /api/v1/lessons/{plan_id}", test_get_plan_backend)

# 8b. Get Lesson Plan via frontend route /api/v1/lessons/plan/{plan_id}
def test_get_plan_frontend_route():
    r = requests.get(f"{BASE_URL}/api/v1/lessons/plan/{plan_id}")
    return {"status_code": r.status_code, "body": r.text[:200]}
run_test("GET /api/v1/lessons/plan/{plan_id} (Frontend api.ts expectation)", test_get_plan_frontend_route)

# 9. Update Lesson Plan via /api/v1/lessons/{plan_id}
def test_update_plan_backend():
    payload = {"title": "Updated Limits Lesson Title"}
    r = requests.put(f"{BASE_URL}/api/v1/lessons/{plan_id}", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("PUT /api/v1/lessons/{plan_id}", test_update_plan_backend)

# 9b. Update Lesson Plan via /api/v1/lessons/plan/{plan_id}
def test_update_plan_frontend_route():
    payload = {"title": "Updated Limits Lesson Title"}
    r = requests.put(f"{BASE_URL}/api/v1/lessons/plan/{plan_id}", json=payload)
    return {"status_code": r.status_code, "body": r.text[:200]}
run_test("PUT /api/v1/lessons/plan/{plan_id} (Frontend api.ts expectation)", test_update_plan_frontend_route)

# 10. Generate Video
task_id = None
def test_generate_video():
    global task_id
    payload = {"plan_id": plan_id}
    r = requests.post(f"{BASE_URL}/api/v1/lessons/generate-video", json=payload)
    assert r.status_code in [200, 202], f"Status {r.status_code}: {r.text}"
    data = r.json()
    task_id = data["task_id"]
    return data
run_test("POST /api/v1/lessons/generate-video", test_generate_video)

# 11. Video Status
def test_video_status():
    r = requests.get(f"{BASE_URL}/api/v1/lessons/video-status/{task_id}")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("GET /api/v1/lessons/video-status/{task_id}", test_video_status)

# 12. Evaluate Answer
def test_evaluate_answer():
    payload = {
        "session_id": "ses_test_001",
        "question_id": "chk_001",
        "student_answer": "A limit only exists if left-hand limit equals right-hand limit.",
        "current_concept": "Foundational Limits",
        "language": "en"
    }
    r = requests.post(f"{BASE_URL}/api/v1/interactive/evaluate", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("POST /api/v1/interactive/evaluate", test_evaluate_answer)

# 13. Tutor Chat
def test_tutor_chat():
    payload = {
        "message": "Can you explain why delta depends on epsilon?",
        "topic_id": topic_id
    }
    r = requests.post(f"{BASE_URL}/api/v1/interactive/chat", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("POST /api/v1/interactive/chat", test_tutor_chat)

# 14. Switch Language
def test_switch_language():
    payload = {
        "session_id": "ses_test_001",
        "target_language": "hi"
    }
    r = requests.post(f"{BASE_URL}/api/v1/interactive/switch-language", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("POST /api/v1/interactive/switch-language", test_switch_language)

# 15. Generate Quiz
quiz_id = None
def test_generate_quiz():
    global quiz_id
    payload = {
        "lesson_id": plan_id,
        "student_id": "stu_test_adaptive",
        "num_questions": 3
    }
    r = requests.post(f"{BASE_URL}/api/v1/assessment/generate", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()
    quiz_id = data["quiz_id"]
    return data
run_test("POST /api/v1/assessment/generate", test_generate_quiz)

# 16. Submit Quiz
submission_id = None
def test_submit_quiz():
    global submission_id
    payload = {
        "quiz_id": quiz_id,
        "student_id": "stu_test_adaptive",
        "lesson_id": plan_id,
        "answers": [
            {"question_id": "quiz_q1", "student_answer": 0},
            {"question_id": "quiz_q2", "student_answer": 0},
            {"question_id": "quiz_q3", "student_answer": "For every epsilon > 0 there exists delta > 0"}
        ]
    }
    r = requests.post(f"{BASE_URL}/api/v1/assessment/submit", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()
    submission_id = data["submission_id"]
    return data
run_test("POST /api/v1/assessment/submit", test_submit_quiz)

# 17. Get Learning Report
def test_get_report():
    r = requests.get(f"{BASE_URL}/api/v1/assessment/report/{submission_id}")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("GET /api/v1/assessment/report/{submission_id}", test_get_report)

# 18. Get Student Profile
def test_get_profile():
    r = requests.get(f"{BASE_URL}/api/v1/profile/stu_test_adaptive")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("GET /api/v1/profile/stu_test_adaptive", test_get_profile)

# 19. Update Student Profile
def test_update_profile():
    payload = {
        "name": "Jane Doe",
        "preferred_level": "advanced",
        "preferred_language": "en"
    }
    r = requests.put(f"{BASE_URL}/api/v1/profile/stu_test_adaptive", json=payload)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("PUT /api/v1/profile/stu_test_adaptive", test_update_profile)

# 20. Get Recommendations
def test_get_recommendations():
    r = requests.get(f"{BASE_URL}/api/v1/profile/stu_test_adaptive/recommendations")
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    return r.json()
run_test("GET /api/v1/profile/stu_test_adaptive/recommendations", test_get_recommendations)

# Save test results
with open("/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_backend/api_test_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nCompleted all tests. Results written to api_test_results.json")
