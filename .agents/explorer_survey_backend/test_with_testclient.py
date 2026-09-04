import os
import sys
import json
import io

sys.path.insert(0, "/home/dev/Desktop/projects/AI-InnovationHackathon")

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

audit_results = {}

print("================================================================")
print("FASTAPI TEST CLIENT AUDIT & ENDPOINT COMPARISON")
print("================================================================")

# 1. GET /api/v1/health
res = client.get("/api/v1/health")
print(f"1. GET /api/v1/health -> Status: {res.status_code}")
audit_results["GET /api/v1/health"] = {
    "status_code": res.status_code,
    "response": res.json()
}

# 2. POST /api/v1/materials/topic
res = client.post("/api/v1/materials/topic", json={
    "topic": "Limits, Continuity & Epsilon-Delta Definition",
    "subject_category": "Mathematics"
})
print(f"2. POST /api/v1/materials/topic -> Status: {res.status_code}")
topic_data = res.json()
topic_id = topic_data.get("topic_id")
audit_results["POST /api/v1/materials/topic"] = {
    "status_code": res.status_code,
    "response": topic_data
}

# 3. POST /api/v1/materials/upload
file_content = b"# Calculus Limits\nA limit is the value that a function approaches as the input approaches some value.\nFormal epsilon-delta definition controls error."
res = client.post("/api/v1/materials/upload", files={
    "file": ("calculus_test.md", io.BytesIO(file_content), "text/markdown")
})
print(f"3. POST /api/v1/materials/upload -> Status: {res.status_code}")
upload_data = res.json()
doc_id = upload_data.get("document_id")
audit_results["POST /api/v1/materials/upload"] = {
    "status_code": res.status_code,
    "response": upload_data
}

# 4. GET /api/v1/materials/{doc_id}
res = client.get(f"/api/v1/materials/{doc_id}")
print(f"4. GET /api/v1/materials/{doc_id} -> Status: {res.status_code}")
audit_results["GET /api/v1/materials/{doc_id}"] = {
    "status_code": res.status_code,
    "response": res.json()
}

# 5. GET /api/v1/materials
res = client.get("/api/v1/materials")
print(f"5. GET /api/v1/materials -> Status: {res.status_code}, count: {len(res.json())}")
audit_results["GET /api/v1/materials"] = {
    "status_code": res.status_code,
    "count": len(res.json()),
    "sample": res.json()[:2] if res.json() else []
}

# 6. POST /api/v1/materials/query
res = client.post("/api/v1/materials/query", json={
    "document_id": doc_id,
    "query": "epsilon delta limit",
    "top_k": 3
})
print(f"6. POST /api/v1/materials/query -> Status: {res.status_code}")
audit_results["POST /api/v1/materials/query"] = {
    "status_code": res.status_code,
    "response": res.json()
}

# 7. POST /api/v1/lessons/plan
res = client.post("/api/v1/lessons/plan", json={
    "learner_profile": {
        "student_id": "stu_audit_001",
        "level": "intermediate",
        "language": "en",
        "time_budget_min": 15
    },
    "topic_id": topic_id
})
print(f"7. POST /api/v1/lessons/plan -> Status: {res.status_code}")
plan_data = res.json()
plan_id = plan_data.get("plan_id")
audit_results["POST /api/v1/lessons/plan"] = {
    "status_code": res.status_code,
    "response_keys": list(plan_data.keys()),
    "sample_module": plan_data.get("modules", [{}])[0] if plan_data.get("modules") else None
}

# 8. GET /api/v1/lessons/{plan_id} (Backend route)
res_b = client.get(f"/api/v1/lessons/{plan_id}")
print(f"8a. GET /api/v1/lessons/{plan_id} (Backend route) -> Status: {res_b.status_code}")
audit_results["GET /api/v1/lessons/{plan_id}"] = {
    "status_code": res_b.status_code,
    "success": res_b.status_code == 200
}

# 8b. GET /api/v1/lessons/plan/{plan_id} (Frontend api.ts expectation)
res_f = client.get(f"/api/v1/lessons/plan/{plan_id}")
print(f"8b. GET /api/v1/lessons/plan/{plan_id} (Frontend route) -> Status: {res_f.status_code}")
audit_results["GET /api/v1/lessons/plan/{plan_id} [Frontend api.ts]"] = {
    "status_code": res_f.status_code,
    "success": res_f.status_code == 200,
    "error_detail": res_f.json() if res_f.status_code != 200 else None
}

# 9a. PUT /api/v1/lessons/{plan_id} (Backend route)
res_ub = client.put(f"/api/v1/lessons/{plan_id}", json={"title": "Updated Title"})
print(f"9a. PUT /api/v1/lessons/{plan_id} (Backend route) -> Status: {res_ub.status_code}")
audit_results["PUT /api/v1/lessons/{plan_id}"] = {
    "status_code": res_ub.status_code,
    "success": res_ub.status_code == 200
}

# 9b. PUT /api/v1/lessons/plan/{plan_id} (Frontend api.ts expectation)
res_uf = client.put(f"/api/v1/lessons/plan/{plan_id}", json={"title": "Updated Title"})
print(f"9b. PUT /api/v1/lessons/plan/{plan_id} (Frontend route) -> Status: {res_uf.status_code}")
audit_results["PUT /api/v1/lessons/plan/{plan_id} [Frontend api.ts]"] = {
    "status_code": res_uf.status_code,
    "success": res_uf.status_code == 200,
    "error_detail": res_uf.json() if res_uf.status_code != 200 else None
}

# 10. GET /api/v1/lessons
res = client.get("/api/v1/lessons")
print(f"10. GET /api/v1/lessons -> Status: {res.status_code}, count: {len(res.json())}")
audit_results["GET /api/v1/lessons"] = {
    "status_code": res.status_code,
    "count": len(res.json())
}

# 11. POST /api/v1/interactive/evaluate
res = client.post("/api/v1/interactive/evaluate", json={
    "session_id": "ses_audit_001",
    "question_id": "chk_001",
    "student_answer": "Limits describe behaviour near a point, not necessarily at the point.",
    "current_concept": "Foundational Limits",
    "language": "en"
})
print(f"11. POST /api/v1/interactive/evaluate -> Status: {res.status_code}")
eval_data = res.json()
audit_results["POST /api/v1/interactive/evaluate"] = {
    "status_code": res.status_code,
    "response": eval_data
}

# 12. POST /api/v1/interactive/chat
res = client.post("/api/v1/interactive/chat", json={
    "message": "Explain what epsilon represents in intuitive terms.",
    "topic_id": topic_id
})
print(f"12. POST /api/v1/interactive/chat -> Status: {res.status_code}")
chat_data = res.json()
audit_results["POST /api/v1/interactive/chat"] = {
    "status_code": res.status_code,
    "response": chat_data
}

# 13. POST /api/v1/interactive/switch-language
res = client.post("/api/v1/interactive/switch-language", json={
    "session_id": "ses_audit_001",
    "target_language": "hi"
})
print(f"13. POST /api/v1/interactive/switch-language -> Status: {res.status_code}")
lang_data = res.json()
audit_results["POST /api/v1/interactive/switch-language"] = {
    "status_code": res.status_code,
    "response": lang_data
}

# 14. GET /api/v1/interactive/session/{session_id}
res = client.get("/api/v1/interactive/session/ses_audit_001")
print(f"14. GET /api/v1/interactive/session/ses_audit_001 -> Status: {res.status_code}")
audit_results["GET /api/v1/interactive/session/{session_id}"] = {
    "status_code": res.status_code,
    "response": res.json()
}

# 15. POST /api/v1/assessment/generate
res = client.post("/api/v1/assessment/generate", json={
    "lesson_id": plan_id,
    "student_id": "stu_audit_learner",
    "num_questions": 3
})
print(f"15. POST /api/v1/assessment/generate -> Status: {res.status_code}")
quiz_data = res.json()
quiz_id = quiz_data.get("quiz_id")
audit_results["POST /api/v1/assessment/generate"] = {
    "status_code": res.status_code,
    "response": quiz_data
}

# 16. POST /api/v1/assessment/submit (Adaptive Loop Trigger)
answers_payload = [
    {"question_id": "quiz_q1", "student_answer": 0},
    {"question_id": "quiz_q2", "student_answer": 0},
    {"question_id": "quiz_q3", "student_answer": "For every epsilon > 0 there exists delta > 0 such that |f(x) - L| < epsilon"}
]
res = client.post("/api/v1/assessment/submit", json={
    "quiz_id": quiz_id,
    "student_id": "stu_audit_learner",
    "lesson_id": plan_id,
    "answers": answers_payload
})
print(f"16. POST /api/v1/assessment/submit -> Status: {res.status_code}")
report_data = res.json()
submission_id = report_data.get("submission_id")
audit_results["POST /api/v1/assessment/submit"] = {
    "status_code": res.status_code,
    "response": report_data
}

# 17. GET /api/v1/assessment/report/{submission_id}
res = client.get(f"/api/v1/assessment/report/{submission_id}")
print(f"17. GET /api/v1/assessment/report/{submission_id} -> Status: {res.status_code}")
audit_results["GET /api/v1/assessment/report/{submission_id}"] = {
    "status_code": res.status_code,
    "response": res.json()
}

# 18. GET /api/v1/profile/{id} (Verify Adaptive Loop Profile Update)
res = client.get("/api/v1/profile/stu_audit_learner")
print(f"18. GET /api/v1/profile/stu_audit_learner -> Status: {res.status_code}")
prof_data = res.json()
audit_results["GET /api/v1/profile/{id}"] = {
    "status_code": res.status_code,
    "response": prof_data
}

# 19. PUT /api/v1/profile/{id}
res = client.put("/api/v1/profile/stu_audit_learner", json={
    "name": "Alex Student",
    "preferred_level": "advanced",
    "preferred_language": "hi"
})
print(f"19. PUT /api/v1/profile/{id} -> Status: {res.status_code}")
audit_results["PUT /api/v1/profile/{id}"] = {
    "status_code": res.status_code,
    "response": res.json()
}

# 20. GET /api/v1/profile/{id}/recommendations (Verify Recommendations)
res = client.get("/api/v1/profile/stu_audit_learner/recommendations")
print(f"20. GET /api/v1/profile/{id}/recommendations -> Status: {res.status_code}")
recs_data = res.json()
audit_results["GET /api/v1/profile/{id}/recommendations"] = {
    "status_code": res.status_code,
    "response": recs_data
}

with open("/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_backend/audit_testclient_results.json", "w") as f:
    json.dump(audit_results, f, indent=2)

print("\nSaved full audit test results to audit_testclient_results.json")
