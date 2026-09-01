## 2026-09-01T00:59:39+05:30
You are worker_m2_planner.
Your working directory is /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m2_planner/
Read ORIGINAL_REQUEST.md at /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md
Read PROJECT.md at /home/dev/Desktop/projects/AI-InnovationHackathon/PROJECT.md
Read M1 handoff at /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_ingestion/handoff.md
Read survey reports at /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_1/handoff.md and /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/spec_miner_survey_3/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your objective:
Implement Milestone 2 (M2: Personalized Lesson Planning Engine) completely and authentically:
1. `backend/app/models/lesson_plan.py`: Pydantic models for `LearnerLevel` (beginner, intermediate, advanced), `LearnerProfile` (student_id, level, language, time_budget_min, prior_knowledge, learning_goal), `VisualType` (math_equation, code_snippet, diagram, timeline, comparison_table, key_takeaways), `VisualSpec` (subject_domain, headline, bullet_points, code_content, code_language, latex_equations, diagram_mermaid, timeline_events), `CheckpointQuestion` (question_id, question_text, question_type, options, correct_answer, explanation, concept, difficulty), `LessonSegmentPlan` (segment_id, order, segment_type, title, duration_sec, script, visual_spec, checkpoint_question), `LessonPlan` (plan_id, title, target_duration_sec, level, language, document_id, topic_id, modules, created_at), `LessonPlanUpdateRequest`.
2. `backend/app/services/planner_service.py`: Pedagogical planning engine:
   - Queries M1 RAG index or topic seed chunks for grounded educational concepts.
   - Adapts concept complexity, vocabulary, and derivation depth based on `LearnerLevel` (Beginner = intuitive analogies + fundamentals; Intermediate = standard rigor + practical applications; Advanced = formal proofs/deep theory + edge cases).
   - Duration scaling based on `time_budget_min` (e.g. 5m budget = 2 core concepts with rapid visual cards; 15m = 3-4 concepts + 2 checkpoints; 30m = 5-6 concepts + demonstrations; 60m = comprehensive 7-8 concept syllabus).
   - Generates domain-aware visual specifications (Math LaTeX formulas, Python/JS syntax-highlighted code blocks, Mermaid diagrams, historical timelines).
   - Assigns check-for-understanding pause checkpoints at logical pedagogical junctures.
   - Supports offline / test mode fallback with deterministic pedagogical templates when external LLM API is unavailable.
3. `backend/app/api/lessons.py`: REST routes:
   - `POST /api/v1/lessons/plan`: Generate lesson plan from document_id or topic with learner_profile.
   - `GET /api/v1/lessons/{plan_id}`: Fetch saved lesson plan.
   - `PUT /api/v1/lessons/{plan_id}`: Update / reorder / edit lesson plan concepts.
   - `GET /api/v1/lessons`: List generated lesson plans.
4. Mount `lessons_router` in `backend/app/main.py`.
5. `backend/tests/test_planner.py`: Comprehensive test suite verifying beginner vs advanced depth, 5m vs 60m duration scaling, multilingual lesson plan generation (English & Hindi), visual spec generation for math/code/diagrams, plan update/reorder endpoints, and edge cases.
6. Run `pytest backend/tests/ -v` and verify all tests pass.
7. Write your handoff to /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m2_planner/handoff.md and notify parent via send_message.
