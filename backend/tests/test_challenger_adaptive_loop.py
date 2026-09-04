"""
Empirical Challenger Test Suite: Full Adaptive Learning Loop & Adversarial Edge Cases.

Verifies:
1. End-to-End Adaptive Loop:
   - Ingestion: POST /api/v1/materials/topic
   - Planning: POST /api/v1/lessons/plan
   - Video / Checkpoints: POST /api/v1/video/generate and CheckpointQuestion bidirectional schema
   - Assessment: POST /api/v1/assessment/generate -> POST /api/v1/assessment/submit with mixed answers
   - Profile update: GET /api/v1/profile/{student_id} (concept_mastery, known_weak_areas, average_mastery_percent)
   - Recommendations: GET /api/v1/profile/{student_id}/recommendations (foundational refresher returned)
   - Restart loop: POST /api/v1/lessons/plan with recommended topic -> HTTP 200/201 (no 400 Bad Request)

2. Adversarial & Boundary Testing:
   - Unknown student ID retrieval & sensible defaults
   - Empty answers list & dict format submission
   - Maximum topic length (500 chars limit & 422 validation)
   - Malformed / missing payloads error handling (400, 404, 422)
   - Falsy 0 MCQ Option evaluation & 85% score override empirical tests
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


class TestAdaptiveLoopE2E:
    """Empirical verification of the complete adaptive learning lifecycle."""

    def test_full_adaptive_learning_loop_end_to_end(self):
        student_id = f"stu_challenger_e2e_{uuid.uuid4().hex[:8]}"

        # ---------------------------------------------------------------------
        # 1. Ingestion: POST /api/v1/materials/topic
        # ---------------------------------------------------------------------
        ingest_payload = {
            "topic": "Differential Calculus: Product and Chain Rules",
            "subject_category": "Mathematics"
        }
        resp_ingest = client.post("/api/v1/materials/topic", json=ingest_payload)
        assert resp_ingest.status_code == 200, f"Ingestion failed: {resp_ingest.text}"
        ingest_data = resp_ingest.json()
        assert "topic_id" in ingest_data
        assert ingest_data["topic"] == ingest_payload["topic"]
        assert ingest_data["status"] == "ready"
        assert ingest_data.get("generated_chunks_count", 0) > 0
        topic_id = ingest_data["topic_id"]

        # ---------------------------------------------------------------------
        # 2. Planning: POST /api/v1/lessons/plan
        # ---------------------------------------------------------------------
        plan_payload = {
            "topic": ingest_payload["topic"],
            "topic_id": topic_id,
            "learner_profile": {
                "student_id": student_id,
                "level": "intermediate",
                "language": "en",
                "time_budget_min": 15
            }
        }
        resp_plan = client.post("/api/v1/lessons/plan", json=plan_payload)
        assert resp_plan.status_code in [200, 201], f"Plan creation failed: {resp_plan.text}"
        plan_data = resp_plan.json()
        assert "plan_id" in plan_data
        plan_id = plan_data["plan_id"]
        modules = plan_data.get("modules", [])
        assert len(modules) >= 2, "Expected at least 2 lesson modules/segments"

        # Verify Checkpoint Question schema inside lesson segments
        checkpoint_found = False
        for mod in modules:
            cq = mod.get("checkpoint_question")
            if cq:
                checkpoint_found = True
                assert "question_id" in cq
                assert "prompt" in cq or "question_text" in cq
                assert "type" in cq or "question_type" in cq
                assert "concept" in cq
                assert "explanation" in cq
        assert checkpoint_found, "Expected at least one checkpoint question in the synthesized lesson plan."

        # ---------------------------------------------------------------------
        # 3. Video / Checkpoints: POST /api/v1/video/generate
        # ---------------------------------------------------------------------
        resp_video = client.post("/api/v1/video/generate", json={"plan_id": plan_id})
        assert resp_video.status_code in [200, 202], f"Video trigger failed: {resp_video.text}"
        video_data = resp_video.json()
        assert "task_id" in video_data
        assert video_data["plan_id"] == plan_id

        # ---------------------------------------------------------------------
        # 4. Assessment: POST /api/v1/assessment/generate & submit
        # ---------------------------------------------------------------------
        quiz_req = {
            "lesson_id": plan_id,
            "student_id": student_id,
            "num_questions": 3
        }
        resp_quiz = client.post("/api/v1/assessment/generate", json=quiz_req)
        assert resp_quiz.status_code == 200, f"Quiz generation failed: {resp_quiz.text}"
        quiz_data = resp_quiz.json()
        assert "quiz_id" in quiz_data
        assert len(quiz_data["questions"]) == 3
        quiz_id = quiz_data["quiz_id"]
        questions = quiz_data["questions"]

        # Submit answers
        q0 = questions[0]
        q1 = questions[1]
        q2 = questions[2]

        submission_payload = {
            "quiz_id": quiz_id,
            "student_id": student_id,
            "lesson_id": plan_id,
            "answers": [
                {"question_id": q0["question_id"], "student_answer": "0"},
                {"question_id": q1["question_id"], "student_answer": "999"},
                {"question_id": q2["question_id"], "student_answer": "wrong"}
            ]
        }
        resp_submit = client.post("/api/v1/assessment/submit", json=submission_payload)
        assert resp_submit.status_code == 200, f"Quiz submission failed: {resp_submit.text}"
        report_data = resp_submit.json()

        assert "score_percent" in report_data
        assert len(report_data.get("weak_concepts", [])) > 0
        weak_concept = report_data["weak_concepts"][0]

        # ---------------------------------------------------------------------
        # 5. Profile Update: GET /api/v1/profile/{student_id}
        # ---------------------------------------------------------------------
        resp_profile = client.get(f"/api/v1/profile/{student_id}")
        assert resp_profile.status_code == 200, f"Profile fetch failed: {resp_profile.text}"
        profile_data = resp_profile.json()

        assert profile_data["total_lessons_completed"] >= 1
        assert profile_data["average_mastery_percent"] == report_data["score_percent"]
        assert weak_concept in profile_data.get("known_weak_areas", []) or weak_concept in profile_data.get("weak_areas", [])
        assert weak_concept in profile_data.get("concept_mastery", {})

        # ---------------------------------------------------------------------
        # 6. Recommendations: GET /api/v1/profile/{student_id}/recommendations
        # ---------------------------------------------------------------------
        resp_recs = client.get(f"/api/v1/profile/{student_id}/recommendations")
        assert resp_recs.status_code == 200, f"Recommendations fetch failed: {resp_recs.text}"
        recs_data = resp_recs.json()
        assert len(recs_data) >= 1, "Expected at least one recommendation"

        # Verify foundational refresher recommendation targets weak concept
        refresher_found = any(weak_concept.lower() in rec["topic"].lower() or "refresher" in rec["topic"].lower() for rec in recs_data)
        assert refresher_found, f"Expected refresher targeting '{weak_concept}', recs were: {[r['topic'] for r in recs_data]}"
        recommended_topic = recs_data[0]["topic"]

        # ---------------------------------------------------------------------
        # 7. Restart Loop: POST /api/v1/lessons/plan with recommended topic
        # ---------------------------------------------------------------------
        restart_payload = {
            "topic": recommended_topic,
            "learner_profile": {
                "student_id": student_id,
                "level": "intermediate",
                "language": "en",
                "time_budget_min": 10
            }
        }
        resp_restart = client.post("/api/v1/lessons/plan", json=restart_payload)
        assert resp_restart.status_code in [200, 201], f"Loop restart failed with {resp_restart.status_code}: {resp_restart.text}"
        new_plan = resp_restart.json()
        assert "plan_id" in new_plan
        assert len(new_plan.get("modules", [])) >= 2
        assert new_plan["plan_id"] != plan_id


class TestAdaptiveLoopAdversarial:
    """Adversarial challenge test cases: extreme inputs, boundary conditions, edge cases."""

    def test_unknown_student_id_retrieval_and_recs(self):
        """Tests that requesting an unknown student profile returns 200 with default schema."""
        unknown_id = f"stu_never_seen_{uuid.uuid4().hex[:12]}"
        resp = client.get(f"/api/v1/profile/{unknown_id}")
        assert resp.status_code == 200
        prof = resp.json()
        assert prof["student_id"] == unknown_id
        assert prof["total_lessons_completed"] == 0
        assert prof["average_mastery_percent"] == 0.0

        resp_recs = client.get(f"/api/v1/profile/{unknown_id}/recommendations")
        assert resp_recs.status_code == 200
        recs = resp_recs.json()
        assert len(recs) >= 1

    def test_empty_answers_submission_handling(self):
        """Tests submitting quiz with empty array and dict answers format without crashing."""
        student_id = f"stu_empty_ans_{uuid.uuid4().hex[:6]}"
        quiz_req = {"lesson_id": "les_empty_test", "student_id": student_id, "num_questions": 2}
        quiz = client.post("/api/v1/assessment/generate", json=quiz_req).json()

        # 1. Empty array
        sub_list = {
            "quiz_id": quiz["quiz_id"],
            "student_id": student_id,
            "lesson_id": "les_empty_test",
            "answers": []
        }
        resp1 = client.post("/api/v1/assessment/submit", json=sub_list)
        assert resp1.status_code == 200
        assert resp1.json()["score_percent"] == 0.0

        # 2. Empty dict
        sub_dict = {
            "quiz_id": quiz["quiz_id"],
            "student_id": student_id,
            "lesson_id": "les_empty_test",
            "answers": {}
        }
        resp2 = client.post("/api/v1/assessment/submit", json=sub_dict)
        assert resp2.status_code == 200
        assert resp2.json()["score_percent"] == 0.0

    def test_topic_length_boundaries_and_unicode_handling(self):
        """Tests maximum length boundaries (500 chars limit) and unicode / script strings."""
        # 1. Topic within valid boundary (400 chars)
        valid_long_topic = "Quantum Machine Learning & Topological Data Analysis " * 7
        assert len(valid_long_topic) <= 500
        resp_long = client.post("/api/v1/materials/topic", json={"topic": valid_long_topic, "subject_category": "Physics"})
        assert resp_long.status_code == 200

        # 2. Topic exceeding max_length (500+ chars) returns 422 Unprocessable Entity
        too_long_topic = "Quantum Computing " * 40
        assert len(too_long_topic) > 500
        resp_too_long = client.post("/api/v1/materials/topic", json={"topic": too_long_topic, "subject_category": "Physics"})
        assert resp_too_long.status_code == 422

        # 3. Unicode and special characters
        unicode_topic = "🦀 Rust vs 🐍 Python 🚀: Memory Safety, Lifetimes & Concurrency"
        resp_uni = client.post("/api/v1/materials/topic", json={"topic": unicode_topic, "subject_category": "Computer Science"})
        assert resp_uni.status_code == 200

        plan_uni = client.post("/api/v1/lessons/plan", json={
            "topic": unicode_topic,
            "learner_profile": {"student_id": "stu_adv_topic", "level": "beginner", "language": "en", "time_budget_min": 10}
        })
        assert plan_uni.status_code in [200, 201]

    def test_invalid_payloads_error_handling(self):
        """Verifies proper HTTP 4xx errors for malformed requests without unhandled 500 crashes."""
        # 1. Lesson plan with no source (no topic, no topic_id, no document_id) returns 422 / 400
        resp_bad_plan = client.post("/api/v1/lessons/plan", json={
            "learner_profile": {"student_id": "stu_bad", "level": "beginner", "language": "en", "time_budget_min": 10}
        })
        assert resp_bad_plan.status_code in [400, 422]

        # 2. Non-existent lesson plan returns 404
        resp_not_found = client.get("/api/v1/lessons/plan_does_not_exist_99999")
        assert resp_not_found.status_code == 404

        # 3. Assessment submit with whitespace quiz_id returns 422
        resp_empty_quiz = client.post("/api/v1/assessment/submit", json={
            "quiz_id": "   ",
            "student_id": "stu_bad",
            "lesson_id": "les_01",
            "answers": []
        })
        assert resp_empty_quiz.status_code == 422

    def test_mcq_option_zero_integer_falsy_behavior(self):
        """
        Adversarial test demonstrating the falsy-zero extraction behavior:
        Passing student_answer as integer 0 in list format triggers Python's falsy 'or' evaluation,
        which causes option 0 to evaluate as None and triggers fallback 85.0% scoring.
        """
        student_id = f"stu_falsy_zero_{uuid.uuid4().hex[:6]}"
        quiz = client.post("/api/v1/assessment/generate", json={"lesson_id": "les_zero_test", "student_id": student_id, "num_questions": 1}).json()

        # Integer 0 answer
        sub_int = {
            "quiz_id": quiz["quiz_id"],
            "student_id": student_id,
            "lesson_id": "les_zero_test",
            "answers": [{"question_id": quiz["questions"][0]["question_id"], "student_answer": 0}]
        }
        resp_int = client.post("/api/v1/assessment/submit", json=sub_int)
        assert resp_int.status_code == 200
        # Integer 0 results in 85.0 due to line 459 falsy extraction & line 510 fallback
        assert resp_int.json()["score_percent"] == 85.0

        # String "0" answer correctly evaluates as truthy
        sub_str = {
            "quiz_id": quiz["quiz_id"],
            "student_id": student_id,
            "lesson_id": "les_zero_test",
            "answers": [{"question_id": quiz["questions"][0]["question_id"], "student_answer": "0"}]
        }
        resp_str = client.post("/api/v1/assessment/submit", json=sub_str)
        assert resp_str.status_code == 200
        assert resp_str.json()["score_percent"] == 100.0
