import requests
import json

BASE_URL = "http://localhost:8000"

print("--- Testing Assessment, Profile, and Adaptive Loop ---")

# 1. Generate Quiz
res1 = requests.post(f"{BASE_URL}/api/v1/assessment/generate", json={
    "lesson_id": "plan_93bf4fdd6f",
    "student_id": "stu_adaptive_survey",
    "num_questions": 3
})
print("1. POST /api/v1/assessment/generate -> Status:", res1.status_code)
quiz_data = res1.json()
print("Quiz response keys:", list(quiz_data.keys()))
print("Questions count:", len(quiz_data.get("questions", [])))
if quiz_data.get("questions"):
    print("Sample question keys:", list(quiz_data["questions"][0].keys()))
    print("Sample question:", json.dumps(quiz_data["questions"][0], indent=2))

# 2. Submit Quiz with answers
answers_payload = [
    {"question_id": "quiz_q1", "student_answer": 0},
    {"question_id": "quiz_q2", "student_answer": 0},
    {"question_id": "quiz_q3", "student_answer": "For every epsilon > 0 there exists delta > 0"}
]
res2 = requests.post(f"{BASE_URL}/api/v1/assessment/submit", json={
    "quiz_id": quiz_data.get("quiz_id", "quiz_default"),
    "student_id": "stu_adaptive_survey",
    "lesson_id": "plan_93bf4fdd6f",
    "answers": answers_payload
})
print("\n2. POST /api/v1/assessment/submit -> Status:", res2.status_code)
report_data = res2.json()
print("Report response keys:", list(report_data.keys()))
print("Report summary:", report_data.get("learning_report_summary"))
print("Score percent:", report_data.get("score_percent"))
print("Strong concepts:", report_data.get("strong_concepts"))
print("Weak concepts:", report_data.get("weak_concepts"))
print("Recommended next topics:", json.dumps(report_data.get("recommended_next_topics"), indent=2))

# 3. Get Student Profile
res3 = requests.get(f"{BASE_URL}/api/v1/profile/stu_adaptive_survey")
print("\n3. GET /api/v1/profile/stu_adaptive_survey -> Status:", res3.status_code)
profile_data = res3.json()
print("Profile keys:", list(profile_data.keys()))
print("Total lessons completed:", profile_data.get("total_lessons_completed"))
print("Average mastery percent:", profile_data.get("average_mastery_percent"))
print("Concept mastery:", profile_data.get("concept_mastery"))
print("Known weak areas:", profile_data.get("known_weak_areas"))
print("Weak areas:", profile_data.get("weak_areas"))
print("Learning history length:", len(profile_data.get("learning_history", [])))

# 4. Get Recommendations
res4 = requests.get(f"{BASE_URL}/api/v1/profile/stu_adaptive_survey/recommendations")
print("\n4. GET /api/v1/profile/stu_adaptive_survey/recommendations -> Status:", res4.status_code)
recs_data = res4.json()
print("Recommendations count:", len(recs_data))
print("Recommendations:", json.dumps(recs_data, indent=2))

# 5. Interactive Evaluate
res5 = requests.post(f"{BASE_URL}/api/v1/interactive/evaluate", json={
    "session_id": "ses_survey_001",
    "question_id": "chk_001",
    "student_answer": "Limit exists if left and right limits are equal",
    "current_concept": "Foundational Limits",
    "language": "en"
})
print("\n5. POST /api/v1/interactive/evaluate -> Status:", res5.status_code)
eval_data = res5.json()
print("Eval keys:", list(eval_data.keys()))
print("Eval data:", json.dumps(eval_data, indent=2))

# 6. Interactive Chat
res6 = requests.post(f"{BASE_URL}/api/v1/interactive/chat", json={
    "message": "Why is calculus important?",
    "topic_id": "top_ca0eb57600"
})
print("\n6. POST /api/v1/interactive/chat -> Status:", res6.status_code)
chat_data = res6.json()
print("Chat keys:", list(chat_data.keys()))
print("Chat reply:", chat_data.get("reply"))

# 7. Interactive Switch Language
res7 = requests.post(f"{BASE_URL}/api/v1/interactive/switch-language", json={
    "session_id": "ses_survey_001",
    "target_language": "hi"
})
print("\n7. POST /api/v1/interactive/switch-language -> Status:", res7.status_code)
lang_data = res7.json()
print("Lang switch data:", json.dumps(lang_data, indent=2))

