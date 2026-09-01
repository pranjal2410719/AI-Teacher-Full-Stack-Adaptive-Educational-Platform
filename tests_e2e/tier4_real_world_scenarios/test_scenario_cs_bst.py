"""
Tier 4 Real-World Scenario: College Computer Science in English (Binary Search Trees)
Persona: Elena (College Sophomore / CS Major)
Goal: Understand BST Operations, Python Implementation, and Time Complexity.
Journey: Upload DOCX -> English Lesson Plan -> Code Slide Specs -> Checkpoint Misconception Diagnosis -> Re-explanation -> Quiz -> Next-Topic Recommendation.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_scenario_college_cs_binary_search_trees(harness, cs_docx_path):
    student_id = "stu_elena_cs_bst"

    # Step 1: Upload authentic BST DOCX
    upload_res = harness.upload_material(cs_docx_path)
    assert upload_res["status_code"] == 200
    doc_id = upload_res["data"]["document_id"]

    # Step 2: Configure learner profile for Intermediate in English with 10-minute budget
    profile = {
        "student_id": student_id,
        "level": "intermediate",
        "language": "en",
        "time_budget_min": 10,
        "prior_knowledge": "Python syntax, recursion, basic arrays",
        "learning_goal": "Master BST recursive insertion and search complexity"
    }
    plan_res = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)
    assert plan_res["status_code"] == 200
    plan = plan_res["data"]
    plan_id = plan["plan_id"]
    assert plan["target_duration_sec"] == 600

    # Verify code visual spec exists
    code_mods = [m for m in plan["modules"] if m["visual_spec"]["visual_type"] == "code_snippet"]
    assert len(code_mods) >= 1
    assert "TreeNode" in code_mods[0]["visual_spec"]["code_content"] or "def insert" in code_mods[0]["visual_spec"]["code_content"]

    # Step 3: Video Generation & Manifest
    task_id = harness.generate_video(plan_id=plan_id)["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]
    manifest = harness.get_video_manifest(lesson_id)["data"]
    assert len(manifest["pause_markers"]) >= 1

    # Step 4: Interactive Checkpoint with Intentional Misconception
    session_id = f"ses_{student_id}"
    wrong_eval = harness.evaluate_answer(
        session_id=session_id,
        question_id=manifest["pause_markers"][0]["question"]["question_id"],
        student_answer="Inserting sorted items into a basic BST still always takes O(log n) time.",
        concept="BST Worst-Case Degeneration"
    )["data"]

    assert wrong_eval["is_correct"] is False
    assert wrong_eval["misconception_detected"] is not None
    assert wrong_eval["pedagogical_re_explanation"] is not None
    assert wrong_eval["follow_up_question"] is not None

    # Step 5: Follow-up question resolution
    follow_up_q = wrong_eval["follow_up_question"]
    correct_eval = harness.evaluate_answer(
        session_id=session_id,
        question_id=follow_up_q["question_id"],
        student_answer="Sorted input degenerates into a linear linked list of O(n) height, which is why balanced trees are used.",
        concept="Balanced BST Invariant"
    )["data"]
    assert correct_eval["is_correct"] is True
    assert correct_eval["can_resume_video"] is True

    # Step 6: Post-Quiz and Learning Report
    quiz = harness.generate_quiz(lesson_id=lesson_id, student_id=student_id, num_questions=2)["data"]
    answers = [
        {"question_id": "quiz_q1", "selected_option_index": 0},
        {"question_id": "quiz_q2", "text_answer": "In-order traversal visits left subtree, root, then right subtree in sorted order."}
    ]
    report = harness.submit_quiz(quiz_id=quiz["quiz_id"], student_id=student_id, lesson_id=lesson_id, answers=answers)["data"]
    assert report["score_percent"] >= 80.0
    assert len(report["recommended_next_topics"]) >= 1
