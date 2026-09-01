"""
Comprehensive Test Suite for Milestone 2: Personalized Lesson Planning Engine.
Tests:
- Model validation & serialization
- Beginner vs Advanced depth and vocabulary calibration
- 5m, 15m, 30m, 60m duration scaling & segment timing
- Multilingual planning (English & Hindi)
- Domain-aware visual specifications (Math LaTeX, CS Code, Bio Mermaid Diagram, History Timeline)
- Prerequisite / Weak concepts injection
- Document-grounded vs Parametric topic planning
- REST API routes (POST, GET, PUT, List) & reordering/editing
- Edge cases and persistence reload
"""

import io
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.models.lesson_plan import (
    LearnerLevel,
    VisualType,
    SegmentType,
    LearnerProfile,
    VisualSpec,
    CheckpointQuestion,
    LessonSegmentPlan,
    LessonPlan,
    LessonPlanCreateRequest,
    LessonPlanUpdateRequest,
    LessonPlanSummary,
)
from backend.app.services.planner_service import planner_service, PlannerService
from backend.app.services.ingestion_service import ingestion_service
from backend.app.models.ingestion import TopicIngestionRequest

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. Pydantic Models Validation Tests
# -----------------------------------------------------------------------------

def test_models_validation():
    """Verifies strict validation and flexible parsing across lesson plan schemas."""
    # LearnerLevel enum & string parsing
    profile = LearnerProfile(
        student_id="student_101",
        level="advanced",  # String coercion to Enum
        language="HI",    # Lowercase cleaner
        time_budget_min=25,
        weak_concepts=["Chain Rule", "Trigonometry"]
    )
    assert profile.level == LearnerLevel.ADVANCED
    assert profile.language == "hi"
    assert profile.time_budget_min == 25
    assert len(profile.weak_concepts) == 2

    # VisualSpec parsing
    v_spec = VisualSpec(
        visual_type="math_equation",
        subject_domain="math",
        headline="Derivatives",
        latex_equations=[r"f'(x) = 2x"]
    )
    assert v_spec.visual_type == VisualType.MATH_EQUATION
    assert len(v_spec.latex_equations) == 1

    # CheckpointQuestion validation
    q = CheckpointQuestion(
        question_id="q1",
        question_text="What is the derivative of x^2?",
        correct_answer="2x",
        explanation="Power rule: 2 * x^(2-1) = 2x",
        concept="Power Rule"
    )
    assert q.difficulty == "medium"
    assert q.question_type == "mcq"

    # Empty question_text should raise ValueError
    with pytest.raises(ValueError):
        CheckpointQuestion(
            question_id="q2",
            question_text="   ",
            correct_answer="2x",
            explanation="...",
            concept="Power Rule"
        )


def test_lesson_plan_create_request_validation():
    """Ensures LessonPlanCreateRequest requires at least one of document_id, topic_id, or topic."""
    # Valid with topic
    req1 = LessonPlanCreateRequest(topic="Calculus")
    assert req1.topic == "Calculus"

    # Valid with document_id
    req2 = LessonPlanCreateRequest(document_id="doc_12345")
    assert req2.document_id == "doc_12345"

    # Invalid with none
    with pytest.raises(ValueError):
        LessonPlanCreateRequest()


# -----------------------------------------------------------------------------
# 2. Beginner vs Advanced Depth & Vocabulary Tests
# -----------------------------------------------------------------------------

def test_beginner_vs_advanced_pedagogical_adaptation():
    """
    Verifies that choosing Beginner vs Advanced produces visibly different
    pedagogical depth, vocabulary, and explanation styles.
    """
    # 1. Beginner Plan
    beg_profile = LearnerProfile(
        student_id="student_beg",
        level=LearnerLevel.BEGINNER,
        time_budget_min=15,
        language="en"
    )
    beg_req = LessonPlanCreateRequest(topic="Calculus Derivatives", learner_profile=beg_profile)
    beg_plan = planner_service.create_lesson_plan(beg_req)

    # 2. Advanced Plan
    adv_profile = LearnerProfile(
        student_id="student_adv",
        level=LearnerLevel.ADVANCED,
        time_budget_min=15,
        language="en"
    )
    adv_req = LessonPlanCreateRequest(topic="Calculus Derivatives", learner_profile=adv_profile)
    adv_plan = planner_service.create_lesson_plan(adv_req)

    assert beg_plan.level == LearnerLevel.BEGINNER
    assert adv_plan.level == LearnerLevel.ADVANCED

    # Combine scripts for vocabulary analysis
    beg_full_script = " ".join(m.script for m in beg_plan.modules).lower()
    adv_full_script = " ".join(m.script for m in adv_plan.modules).lower()

    # Beginner should have conversational / analogy / intuitive phrasing
    assert any(term in beg_full_script for term in ["intuitive", "simple", "everyday", "fun", "easy", "help"])

    # Advanced should have rigorous mathematical / formal terminology
    assert any(term in adv_full_script for term in ["rigorous", "formal", "invariant", "boundary", "foundations", "analysis"])

    # Verify visual specs differ in depth
    beg_math_specs = [m.visual_spec for m in beg_plan.modules if m.visual_spec and m.visual_spec.latex_equations]
    adv_math_specs = [m.visual_spec for m in adv_plan.modules if m.visual_spec and m.visual_spec.latex_equations]

    assert len(beg_math_specs) > 0
    assert len(adv_math_specs) > 0
    # Advanced LaTeX contains multi-variable or limit formulations
    adv_latex_str = " ".join(" ".join(s.latex_equations) for s in adv_math_specs)
    assert any(sym in adv_latex_str for sym in ["\\nabla", "\\lim", "\\partial", "\\mathbf"])


# -----------------------------------------------------------------------------
# 3. Duration Scaling Tests (5m, 15m, 30m, 60m)
# -----------------------------------------------------------------------------

def test_duration_scaling_5min_vs_60min():
    """
    Verifies that time budget scales the number of concepts, segments, and total duration.
    - 5m budget -> ~300s, 2 concepts, micro-lesson
    - 60m budget -> ~3600s, 7+ concepts, masterclass
    """
    # 5 min Plan
    p5_req = LessonPlanCreateRequest(
        topic="Binary Search Algorithm",
        learner_profile=LearnerProfile(time_budget_min=5)
    )
    p5 = planner_service.create_lesson_plan(p5_req)

    # 15 min Plan
    p15_req = LessonPlanCreateRequest(
        topic="Binary Search Algorithm",
        learner_profile=LearnerProfile(time_budget_min=15)
    )
    p15 = planner_service.create_lesson_plan(p15_req)

    # 60 min Plan
    p60_req = LessonPlanCreateRequest(
        topic="Binary Search Algorithm",
        learner_profile=LearnerProfile(time_budget_min=60)
    )
    p60 = planner_service.create_lesson_plan(p60_req)

    # Total duration precision
    assert p5.target_duration_sec == 300
    assert p5.total_actual_duration_sec == 300
    assert p15.target_duration_sec == 900
    assert p15.total_actual_duration_sec == 900
    assert p60.target_duration_sec == 3600
    assert p60.total_actual_duration_sec == 3600

    # Module counts scaling
    assert len(p5.modules) < len(p15.modules) < len(p60.modules)
    assert len(p5.modules) >= 4  # Intro, 2 concepts, summary
    assert len(p60.modules) >= 12  # Intro, 7 concepts, checkpoints, demos, summary

    # Segment order integrity
    for plan in (p5, p15, p60):
        for idx, mod in enumerate(plan.modules, start=1):
            assert mod.order == idx
            assert mod.duration_sec >= 5


# -----------------------------------------------------------------------------
# 4. Domain-Aware Visual Specification Tests
# -----------------------------------------------------------------------------

def test_visual_spec_math_calculus():
    """Verifies math topics generate LaTeX equations and MATH_EQUATION visual specs."""
    req = LessonPlanCreateRequest(topic="Differential Calculus Derivatives")
    plan = planner_service.create_lesson_plan(req)

    assert plan.subject_domain == "math"
    visual_types = [m.visual_spec.visual_type for m in plan.modules if m.visual_spec]
    assert VisualType.MATH_EQUATION in visual_types

    # Check LaTeX content
    math_mods = [m for m in plan.modules if m.visual_spec and m.visual_spec.latex_equations]
    assert len(math_mods) > 0
    for m in math_mods:
        assert len(m.visual_spec.latex_equations) >= 1
        assert any("=" in eq or "frac" in eq or "\\Delta" in eq for eq in m.visual_spec.latex_equations)


def test_visual_spec_computer_science_programming():
    """Verifies computer science topics generate syntax-highlighted code blocks."""
    req = LessonPlanCreateRequest(topic="Binary Search Algorithm and Recursion in Python")
    plan = planner_service.create_lesson_plan(req)

    assert plan.subject_domain == "computer_science"
    cs_mods = [m for m in plan.modules if m.visual_spec and m.visual_spec.code_content]
    assert len(cs_mods) > 0
    for m in cs_mods:
        assert m.visual_spec.visual_type == VisualType.CODE_SNIPPET
        assert m.visual_spec.code_language == "python"
        assert "def " in m.visual_spec.code_content or "=" in m.visual_spec.code_content


def test_visual_spec_biology_diagram():
    """Verifies biology topics generate Mermaid diagram definitions."""
    req = LessonPlanCreateRequest(topic="Photosynthesis and Cellular Respiration in Chloroplasts")
    plan = planner_service.create_lesson_plan(req)

    assert plan.subject_domain == "biology"
    bio_mods = [m for m in plan.modules if m.visual_spec and m.visual_spec.diagram_mermaid]
    assert len(bio_mods) > 0
    for m in bio_mods:
        assert m.visual_spec.visual_type == VisualType.DIAGRAM
        assert "graph TD" in m.visual_spec.diagram_mermaid


def test_visual_spec_history_timeline():
    """Verifies history topics generate chronological timeline events."""
    req = LessonPlanCreateRequest(topic="French Revolution and Constitutional Monarchy")
    plan = planner_service.create_lesson_plan(req)

    assert plan.subject_domain == "history"
    hist_mods = [m for m in plan.modules if m.visual_spec and m.visual_spec.timeline_events]
    assert len(hist_mods) > 0
    for m in hist_mods:
        assert m.visual_spec.visual_type == VisualType.TIMELINE
        assert len(m.visual_spec.timeline_events) >= 2


# -----------------------------------------------------------------------------
# 5. Multilingual Lesson Planning Tests (Hindi & English)
# -----------------------------------------------------------------------------

def test_multilingual_hindi_lesson_plan():
    """
    Verifies that selecting Hindi produces Hindi narration scripts, Devanagari headings,
    and Hindi checkpoint questions.
    """
    req = LessonPlanCreateRequest(
        topic="सौर ऊर्जा और प्रकाश संश्लेषण",
        subject_domain="biology",
        learner_profile=LearnerProfile(
            language="hi",
            level=LearnerLevel.BEGINNER,
            time_budget_min=15
        )
    )
    plan = planner_service.create_lesson_plan(req)

    assert plan.language == "hi"
    intro_seg = plan.modules[0]
    assert "नमस्ते" in intro_seg.script

    # Checkpoint questions in Hindi
    chk_segs = [m for m in plan.modules if m.checkpoint_question is not None]
    assert len(chk_segs) >= 1
    assert any("?" in m.checkpoint_question.question_text or "क्या" in m.checkpoint_question.question_text for m in chk_segs)


# -----------------------------------------------------------------------------
# 6. Prerequisite & Weakness Injection Tests
# -----------------------------------------------------------------------------

def test_prerequisite_refresher_injection():
    """
    Verifies that known student weaknesses (from LearnerProfile.weak_concepts)
    are injected into the lesson's prerequisite refresher list and introductory narration.
    """
    profile = LearnerProfile(
        student_id="student_remedial",
        level=LearnerLevel.INTERMEDIATE,
        time_budget_min=15,
        weak_concepts=["Slope of a line", "Algebraic factoring"]
    )
    req = LessonPlanCreateRequest(
        topic="Calculus Derivatives",
        learner_profile=profile
    )
    plan = planner_service.create_lesson_plan(req)

    assert len(plan.prerequisite_refreshers) >= 2
    assert "Slope of a line" in plan.prerequisite_refreshers
    intro_script = plan.modules[0].script
    assert "Slope of a line" in intro_script


# -----------------------------------------------------------------------------
# 7. Document-Grounded vs Parametric Topic Planning Tests
# -----------------------------------------------------------------------------

def test_document_grounded_lesson_plan():
    """
    Verifies that uploading a document and generating a lesson plan grounds
    the plan in the document's chunk citations and section titles.
    """
    # 1. Ingest sample document
    txt_content = (
        "# Quantum Computing Basics\n\n"
        "Quantum computing harnesses the phenomena of quantum mechanics, such as superposition and entanglement.\n\n"
        "## Qubits and Superposition\n\n"
        "Unlike classical bits which are 0 or 1, a qubit exists in a linear combination state: |psi> = alpha |0> + beta |1|.\n\n"
        "## Quantum Entanglement\n\n"
        "Entangled qubits exhibit correlated states regardless of physical separation distance."
    )
    meta, chunks = ingestion_service.ingest_document(
        file_bytes=txt_content.encode("utf-8"),
        filename="quantum_notes.md"
    )

    # 2. Generate grounded plan
    req = LessonPlanCreateRequest(
        document_id=meta.document_id,
        learner_profile=LearnerProfile(time_budget_min=15, level=LearnerLevel.INTERMEDIATE)
    )
    plan = planner_service.create_lesson_plan(req)

    assert plan.document_id == meta.document_id
    # Check that modules have citations referencing chunks
    cited_chunks = [c for m in plan.modules for c in m.grounding_citations]
    assert len(cited_chunks) > 0


# -----------------------------------------------------------------------------
# 8. REST API Endpoints Tests
# -----------------------------------------------------------------------------

def test_api_create_lesson_plan():
    """Tests POST /api/v1/lessons/plan."""
    payload = {
        "topic": "Newton's Laws of Motion",
        "subject_domain": "physics",
        "learner_profile": {
            "student_id": "std_100",
            "level": "intermediate",
            "language": "en",
            "time_budget_min": 15
        }
    }
    resp = client.post("/api/v1/lessons/plan", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "plan_id" in data
    assert data["target_duration_sec"] == 900
    assert data["total_actual_duration_sec"] == 900
    assert len(data["modules"]) >= 4
    assert data["level"] == "intermediate"


def test_api_get_lesson_plan_and_not_found():
    """Tests GET /api/v1/lessons/{plan_id} for existing and non-existing plans."""
    # 1. Create plan
    req = LessonPlanCreateRequest(topic="Photosynthesis")
    plan = planner_service.create_lesson_plan(req)

    # 2. Get existing plan
    resp = client.get(f"/api/v1/lessons/{plan.plan_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan_id"] == plan.plan_id
    assert data["title"] == plan.title

    # 3. Not found
    resp_404 = client.get("/api/v1/lessons/non_existent_plan_999")
    assert resp_404.status_code == 404
    assert "not found" in resp_404.json()["detail"].lower()


def test_api_update_and_reorder_lesson_plan():
    """Tests PUT /api/v1/lessons/{plan_id} for updating title and reordering segments."""
    # 1. Create plan
    req = LessonPlanCreateRequest(
        topic="Algorithm Sorting Techniques",
        learner_profile=LearnerProfile(time_budget_min=15)
    )
    plan = planner_service.create_lesson_plan(req)
    orig_seg_ids = [m.segment_id for m in plan.modules]
    assert len(orig_seg_ids) >= 3

    # 2. Swap 2nd and 3rd segment
    reordered_ids = list(orig_seg_ids)
    reordered_ids[1], reordered_ids[2] = reordered_ids[2], reordered_ids[1]

    update_payload = {
        "title": "Mastering Advanced Sorting Algorithms",
        "reorder_segment_ids": reordered_ids,
        "level": "advanced"
    }
    resp = client.put(f"/api/v1/lessons/{plan.plan_id}", json=update_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Mastering Advanced Sorting Algorithms"
    assert data["level"] == "advanced"
    new_seg_ids = [m["segment_id"] for m in data["modules"]]
    assert new_seg_ids == reordered_ids
    # Verify orders are 1, 2, 3...
    for idx, m in enumerate(data["modules"], start=1):
        assert m["order"] == idx


def test_api_update_with_invalid_reorder_segment():
    """Verifies that attempting to reorder with an invalid segment ID returns 400 Bad Request."""
    req = LessonPlanCreateRequest(topic="Geometry")
    plan = planner_service.create_lesson_plan(req)

    update_payload = {
        "reorder_segment_ids": ["seg_fake_invalid_id", "seg_fake_2"]
    }
    resp = client.put(f"/api/v1/lessons/{plan.plan_id}", json=update_payload)
    assert resp.status_code == 400
    assert "does not belong" in resp.json()["detail"]


def test_api_list_lesson_plans():
    """Tests GET /api/v1/lessons returns summary list."""
    resp = client.get("/api/v1/lessons")
    assert resp.status_code == 200
    plans_list = resp.json()
    assert isinstance(plans_list, list)
    assert len(plans_list) >= 1
    sample = plans_list[0]
    assert "plan_id" in sample
    assert "target_duration_sec" in sample
    assert "segment_count" in sample


# -----------------------------------------------------------------------------
# 9. Persistence & Disk Reload Tests
# -----------------------------------------------------------------------------

def test_persistence_reload_across_service_instances():
    """Verifies that plans persisted to disk can be reloaded in a fresh PlannerService instance."""
    # 1. Create plan
    req = LessonPlanCreateRequest(
        topic="Organic Chemistry Functional Groups",
        learner_profile=LearnerProfile(time_budget_min=30, level=LearnerLevel.ADVANCED)
    )
    plan = planner_service.create_lesson_plan(req)

    # 2. Instantiate new PlannerService to simulate server restart
    fresh_service = PlannerService()
    reloaded_plan = fresh_service.get_plan(plan.plan_id)

    assert reloaded_plan is not None
    assert reloaded_plan.plan_id == plan.plan_id
    assert reloaded_plan.title == plan.title
    assert reloaded_plan.target_duration_sec == plan.target_duration_sec
    assert len(reloaded_plan.modules) == len(plan.modules)
