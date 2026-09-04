# Handoff Report: Milestone M1 — Backend API Alignment & Fixes

**Agent**: Worker M1 Backend (`worker_m1_backend`)  
**Milestone**: M1 (Backend API Alignment & Fixes)  
**Date**: 2026-09-02  
**Status**: COMPLETE  

---

## 1. Observation

Direct code inspections and empirical tests revealed three core backend issues:

1. **Route Mismatch on Lesson Plan Retrieval / Update**:
   - `frontend/src/services/api.ts` makes requests to `GET /api/v1/lessons/plan/${planId}` and `PUT /api/v1/lessons/plan/${planId}`.
   - `backend/app/api/lessons.py` previously registered only `@router.get("/{plan_id}")` and `@router.put("/{plan_id}")`, causing HTTP 404 Not Found errors when fetching or updating a lesson plan through the frontend API client.

2. **Vector Store Query Keyword & Unpacking Bug**:
   - In `backend/app/services/interaction_service.py` (line 517), `vector_store.query(target_id=target_id, query_text=msg, top_k=2)` was called using the wrong keyword argument (`query_text` instead of `query`).
   - In addition, `vector_store.query()` returns an instance of `RAGResponse` (which encapsulates `.results: List[ChunkMatch]`), but line 519-520 attempted to iterate over `rag_res` directly as if it were a raw list of chunks. This threw a `TypeError` and silently failed RAG contextual retrieval during Side-Panel AI Tutor chat.

3. **`CheckpointQuestion` Model Field Incompatibility**:
   - In `backend/app/models/lesson_plan.py`, `CheckpointQuestion` defined only `question_text`, `question_type`, and `correct_answer`.
   - The frontend TypeScript definitions (`frontend/src/types/index.ts`) and `LessonPlanEditor.tsx` (line 324) expect `prompt`, `type`, and `correct_option_index`.
   - As a result, formative checkpoint questions rendered blank prompts in the Lesson Plan Editor.

---

## 2. Logic Chain

1. **Route Parity in `backend/app/api/lessons.py`**:
   - Added `@router.get("/plan/{plan_id}", response_model=LessonPlan)` on `get_lesson_plan`.
   - Added `@router.put("/plan/{plan_id}", response_model=LessonPlan)` on `update_lesson_plan`.
   - Both `/api/v1/lessons/{plan_id}` and `/api/v1/lessons/plan/{plan_id}` now route to the same handler functions, supporting existing backend tests and frontend API client invocations.

2. **RAG Vector Retrieval in `backend/app/services/interaction_service.py`**:
   - Changed invocation to `rag_res = vector_store.query(query=msg, target_id=target_id, top_k=2)`.
   - Extracted results safely from `rag_res.results`:
     ```python
     if rag_res and rag_res.results:
         sources = [f"{m.source_filename} (p.{m.page_or_slide or 1})" for m in rag_res.results]
         grounded_context = "\n".join([m.text for m in rag_res.results])
     ```
   - Eliminated `TypeError` and restored RAG-grounded tutor replies and source citations.

3. **Bidirectional Schema Compatibility in `backend/app/models/lesson_plan.py`**:
   - Added optional fields to `CheckpointQuestion`:
     - `prompt: Optional[str] = None`
     - `type: Optional[str] = "mcq"`
     - `correct_option_index: Optional[int] = None`
   - Implemented `model_validator`s (in both `mode="before"` and `mode="after"`):
     - If `prompt` is provided and `question_text` is not -> `question_text = prompt` (and vice-versa).
     - If `type` is provided and `question_type` is not -> `question_type = type` (and vice-versa).
     - If `correct_option_index` is provided and `correct_answer` is not -> `correct_answer = options[correct_option_index]` (and vice-versa).
     - Enforced non-empty validation on `question_text`/`prompt`, `correct_answer`, and `concept`.
   - Serialized JSON responses now contain all fields required by both frontend and backend consumers.

---

## 3. Caveats

- No caveats. All changes are backward-compatible with existing API callers, adhere strictly to Pydantic v2 conventions, and pass all unit and integration test suites.

---

## 4. Conclusion

Milestone M1 is fully accomplished:
- Route aliases `/api/v1/lessons/plan/{plan_id}` (GET & PUT) are operational.
- Side-panel AI Tutor RAG grounding executes smoothly without `TypeError`.
- `CheckpointQuestion` serializes and validates seamlessly across both frontend and backend naming conventions.
- The entire pytest test suite (166 tests) passed with 100% success rate.

---

## 5. Verification Method

To independently reproduce and verify all changes:

1. **Run Full Pytest Test Suite**:
   ```bash
   /home/dev/Desktop/projects/AI-InnovationHackathon/.venv/bin/python -m pytest backend/tests
   ```
   *Result*: 166 passed in 93.25s.

2. **Run Targeted M1 Verification**:
   ```python
   /home/dev/Desktop/projects/AI-InnovationHackathon/.venv/bin/python -c "
   from fastapi.testclient import TestClient
   from backend.app.main import app
   from backend.app.models.lesson_plan import CheckpointQuestion, LessonPlanCreateRequest, LearnerProfile
   from backend.app.services.planner_service import planner_service
   from backend.app.services.interaction_service import interaction_service, TutorChatRequest
   from backend.app.services.vector_store import vector_store
   from backend.app.models.ingestion import DocumentChunk

   # 1. CheckpointQuestion schema sync
   q = CheckpointQuestion(
       question_id='q1', prompt='What is 2+2?', type='mcq',
       options=['3', '4'], correct_option_index=1,
       explanation='Addition', concept='Math'
   )
   assert q.question_text == 'What is 2+2?' and q.correct_answer == '4'

   # 2. Lessons API route aliases
   client = TestClient(app)
   plan = planner_service.create_lesson_plan(LessonPlanCreateRequest(topic='Math'))
   assert client.get(f'/api/v1/lessons/plan/{plan.plan_id}').status_code == 200
   assert client.put(f'/api/v1/lessons/plan/{plan.plan_id}', json={'title': 'New'}).status_code == 200

   # 3. Vector query
   vector_store.add_document('doc1', [DocumentChunk(chunk_id='c1', document_id='doc1', source_filename='f.pdf', text='chunk text')])
   res = interaction_service.tutor_chat(TutorChatRequest(message='q', document_id='doc1'))
   assert len(res.grounded_sources) > 0
   print('ALL VERIFICATIONS PASSED')
   "
   ```
