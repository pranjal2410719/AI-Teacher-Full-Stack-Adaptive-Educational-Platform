## 2026-09-02T11:11:28Z
<USER_REQUEST>
You are a Worker implementing Milestone M1: Backend API Alignment & Fixes.

Authoritative Request: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md (READ THIS FIRST)
Survey Report: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_backend/survey_backend_report.md
Project Plan: /home/dev/Desktop/projects/AI-InnovationHackathon/PROJECT.md
Your working directory: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_backend

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Exclusive File Ownership:
- backend/app/api/lessons.py
- backend/app/services/interaction_service.py
- backend/app/models/lesson_plan.py

Your Tasks:
1. In backend/app/api/lessons.py:
   Add route aliases for GET /plan/{plan_id} and PUT /plan/{plan_id} alongside existing /{plan_id} routes:
   - @router.get("/plan/{plan_id}", response_model=LessonPlan) -> get_lesson_plan
   - @router.put("/plan/{plan_id}", response_model=LessonPlan) -> update_lesson_plan
   Ensure both /api/v1/lessons/{plan_id} and /api/v1/lessons/plan/{plan_id} work for GET and PUT.

2. In backend/app/services/interaction_service.py (around line 517):
   Fix the vector search query call:
   Change `rag_res = vector_store.query(target_id=target_id, query_text=msg, top_k=2)` to `rag_res = vector_store.query(query=msg, target_id=target_id, top_k=2)`.
   Ensure results are extracted from `rag_res.results` and formatted into `grounded_context` and `sources` without raising TypeError.

3. In backend/app/models/lesson_plan.py:
   In `CheckpointQuestion` model:
   Add optional fields `prompt: Optional[str] = None`, `type: Optional[str] = "mcq"`, `correct_option_index: Optional[int] = None`.
   Use a model validator or root_validator to ensure:
   - If `prompt` is provided and `question_text` is not, `question_text = prompt` (and vice-versa).
   - If `type` is provided and `question_type` is not, `question_type = type` (and vice-versa).
   - If `correct_option_index` is provided and `correct_answer` is not, calculate `correct_answer = options[correct_option_index]`.

4. Verification:
   Run `/home/dev/Desktop/projects/AI-InnovationHackathon/.venv/bin/python -m pytest backend/tests`
   Ensure all tests pass.
   Write handoff.md in your working directory documenting code changes and test execution outputs.

Communicate completion back to orchestrator via send_message.
</USER_REQUEST>
