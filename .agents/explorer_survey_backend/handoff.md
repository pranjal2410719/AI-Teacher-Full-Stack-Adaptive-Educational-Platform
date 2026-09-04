# Handoff Report: Backend API & Adaptive Loop Survey

## 1. Observation

Direct observations and verbatim test results recorded during the audit:

1. **Test Suite Execution**:
   - Command: `/home/dev/Desktop/projects/AI-InnovationHackathon/.venv/bin/python -m pytest backend/tests`
   - Result: `166 passed, 4 warnings in 104.04s`
   - All unit and integration tests in `backend/tests/` passed successfully.

2. **Route 404 Mismatches**:
   - Frontend API client definition: `frontend/src/services/api.ts` (lines 73-85):
     ```typescript
     async getLessonPlan(planId: string): Promise<LessonPlan> {
       const res = await fetch(`${API_BASE}/lessons/plan/${planId}`);
       return handleResponse<LessonPlan>(res);
     }
     async updateLessonPlan(planId: string, updatedPlan: Partial<LessonPlan>): Promise<LessonPlan> {
       const res = await fetch(`${API_BASE}/lessons/plan/${planId}`, {
         method: 'PUT',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(updatedPlan),
       });
       return handleResponse<LessonPlan>(res);
     }
     ```
   - Backend router definition: `backend/app/api/lessons.py` (lines 58, 77):
     ```python
     router = APIRouter(prefix="/api/v1/lessons", tags=["Lesson Planning & Review"])
     @router.get("/{plan_id}", response_model=LessonPlan)
     @router.put("/{plan_id}", response_model=LessonPlan)
     ```
   - Live HTTP request test:
     - `GET /api/v1/lessons/plan_93bf4fdd6f` -> `200 OK`
     - `GET /api/v1/lessons/plan/plan_93bf4fdd6f` -> `404 Not Found` (Detail: `{"detail": "Not Found"}`)
     - `PUT /api/v1/lessons/plan/plan_93bf4fdd6f` -> `404 Not Found` (Detail: `{"detail": "Not Found"}`)

3. **Tutor Chat Vector Search Exception**:
   - File: `backend/app/services/interaction_service.py` (line 517):
     ```python
     rag_res = vector_store.query(target_id=target_id, query_text=msg, top_k=2)
     ```
   - Method signature: `backend/app/services/vector_store.py` (line 420):
     ```python
     def query(self, query: str, target_id: Optional[str] = None, top_k: int = 4, alpha: float = 0.6) -> RAGResponse:
     ```
   - Verbatim runtime warning in test execution:
     `WARNING:ai_teacher.interaction:Vector search failed in tutor chat: NumpyVectorStore.query() got an unexpected keyword argument 'query_text'`

4. **Model Field Discrepancy in Checkpoint Questions**:
   - Backend: `backend/app/models/lesson_plan.py` (lines 130-144) defines:
     `question_text: str`, `question_type: str = "mcq"`, `correct_answer: str`
   - Frontend: `frontend/src/types/index.ts` (lines 57-65) defines:
     `prompt: string`, `type: 'mcq' | 'short_answer'`, `correct_option_index?: number | null`
   - Component consumption: `frontend/src/components/Planner/LessonPlanEditor.tsx` (line 324):
     `{selectedSegment.checkpoint_question.prompt}` and `i === selectedSegment.checkpoint_question?.correct_option_index`

5. **Adaptive Loop State Verification**:
   - Test executed: `test_assessment_and_profile.py`
   - Assessment Submission: `POST /api/v1/assessment/submit` -> returned `score_percent: 33.3`, `strong_concepts: ['Epsilon-Delta Definition']`, `weak_concepts: ['Foundational Limits', 'Secant vs Tangent Slope Interpretation']`
   - Profile Retrieval: `GET /api/v1/profile/stu_adaptive_survey` -> returned `total_lessons_completed: 1`, `average_mastery_percent: 33.3`, `known_weak_areas: ['Foundational Limits', 'Secant vs Tangent Slope Interpretation']`
   - Recommendations Retrieval: `GET /api/v1/profile/stu_adaptive_survey/recommendations` -> returned 2 items:
     - `Foundational Refresher: Foundational Limits`
     - `Foundational Refresher: Secant vs Tangent Slope Interpretation`

---

## 2. Logic Chain

1. **Route Resolution**:
   - From Observation 2, `api.ts` makes requests to `/api/v1/lessons/plan/{id}`, but `lessons.py` registers routes on `/{id}` under prefix `/api/v1/lessons`.
   - In FastAPI routing, `/api/v1/lessons` + `/{plan_id}` matches `/api/v1/lessons/123`, but does NOT match `/api/v1/lessons/plan/123`.
   - Therefore, any frontend attempt to fetch or update a plan triggers an uncaught 404 error, breaking the Lesson Plan tab whenever a plan is re-fetched or updated.

2. **RAG Grounding in Interactive Tutor**:
   - From Observation 3, `interaction_service.py` calls `vector_store.query()` with the keyword argument `query_text=msg`.
   - `vector_store.query()` expects the positional or keyword argument `query`.
   - Python raises `TypeError`, which is swallowed by the `try-except` block in `interaction_service.py`, returning empty `sources = []` and leaving `grounded_context = ""`.
   - Therefore, tutor chat fails to ground student questions on the ingested curriculum.

3. **UI Checkpoint Question Rendering**:
   - From Observation 4, `LessonPlanEditor.tsx` renders `checkpoint_question.prompt`.
   - When the backend generates a lesson plan, it populates `checkpoint_question.question_text`.
   - In JavaScript/TypeScript, accessing `.prompt` on an object that only has `question_text` yields `undefined`, resulting in blank prompt text in the UI.

4. **Adaptive Loop Closing**:
   - From Observation 5, when `submitQuiz` is called, `profile_service.record_lesson_completion` correctly records mastery scores and weak concepts in both SQLite and JSON files.
   - When the user transitions to the Analytics tab, `profile_service.get_recommendations()` creates targeted refreshers specifically for the weak concepts detected.
   - Clicking a recommendation calls `handleSelectTopicFromDashboard(topic)` in `App.tsx`, completing the loop back to ingestion/planning.

---

## 3. Caveats

1. **Async Video Rendering**: As noted in the prompt, actual end-to-end MP4 video stitching relies on neural TTS (`edge-tts`) and `ffmpeg`. If external network connectivity to MS Edge-TTS is restricted or slow, video generation falls back after timeout to local audio synthesis. This is marked as "best-effort" per audit instructions.
2. **LLM Provider Mode**: When `GROQ_API_KEY` or `GEMINI_API_KEY` is not present, the system operates in `offline_parametric` mode, which uses rule-based and template generators. The API schema and data contracts are identical across both modes.

---

## 4. Conclusion

The FastAPI backend is functionally healthy with 166 passing tests. To achieve complete frontend-backend parity and unblock end-to-end user workflows, three targeted backend fixes are required:
1. Add `@router.get("/plan/{plan_id}")` and `@router.put("/plan/{plan_id}")` route aliases in `backend/app/api/lessons.py`.
2. Fix parameter name from `query_text` to `query` and unwrap `.results` in `backend/app/services/interaction_service.py` (line 517).
3. Add `prompt`, `type`, and `correct_option_index` fields/aliases to `CheckpointQuestion` in `backend/app/models/lesson_plan.py`.

The adaptive feedback loop is fully intact and correctly passes quiz performance into profile mastery and personalized recommendation cards.

---

## 5. Verification Method

1. **Run Pytest**:
   ```bash
   /home/dev/Desktop/projects/AI-InnovationHackathon/.venv/bin/python -m pytest /home/dev/Desktop/projects/AI-InnovationHackathon/backend/tests
   ```
2. **Run Endpoint Audit Script**:
   ```bash
   /home/dev/Desktop/projects/AI-InnovationHackathon/.venv/bin/python /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_backend/test_with_testclient.py
   ```
3. **Inspect Output Files**:
   - Detailed Survey Report: `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_backend/survey_backend_report.md`
   - TestClient Results JSON: `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_backend/audit_testclient_results.json`
   - Live API Results JSON: `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_backend/api_test_results.json`

