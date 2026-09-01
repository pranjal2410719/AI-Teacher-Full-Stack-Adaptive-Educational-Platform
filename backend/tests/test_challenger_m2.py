"""
Empirical Challenger Test Suite for Milestone 2: Personalized Lesson Planning Engine.
Adversarial stress-testing of boundary conditions, unknown types, malformed updates,
Unicode & Devanagari resilience, and HTTP status code verification (zero uncaught 500s).
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
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

client = TestClient(app)


# =============================================================================
# 1. TIME BUDGET BOUNDARY & EXTREME VALUES ADVERSARIAL TESTS
# =============================================================================

class TestTimeBudgetBoundaries:
    """Stress tests on duration budgets, lower/upper bounds, and scaling invariants."""

    def test_time_budget_zero_rejected_with_422(self):
        """POST /api/v1/lessons/plan with time_budget_min=0 must return 422 Unprocessable Entity."""
        payload = {
            "topic": "Calculus Fundamentals",
            "learner_profile": {"time_budget_min": 0}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
        errors = resp.json()["detail"]
        assert any("greater than or equal to 1" in str(e).lower() or "time_budget_min" in str(e).lower() for e in errors)

    def test_time_budget_negative_rejected_with_422(self):
        """POST /api/v1/lessons/plan with time_budget_min=-15 must return 422 Unprocessable Entity."""
        payload = {
            "topic": "Calculus Fundamentals",
            "learner_profile": {"time_budget_min": -15}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"

    def test_time_budget_exceeding_180_rejected_with_422(self):
        """POST /api/v1/lessons/plan with time_budget_min=181 and 1000 must return 422."""
        for extreme_val in [181, 200, 1000, 99999]:
            payload = {
                "topic": "Calculus Fundamentals",
                "learner_profile": {"time_budget_min": extreme_val}
            }
            resp = client.post("/api/v1/lessons/plan", json=payload)
            assert resp.status_code == 422, f"Expected 422 for time_budget_min={extreme_val}, got {resp.status_code}"

    def test_time_budget_exact_lower_bound_1_min(self):
        """1 minute time budget produces exactly 60 seconds with valid segment durations (>= 5s)."""
        payload = {
            "topic": "Quick Micro-concept: Pythagorean Theorem",
            "learner_profile": {"time_budget_min": 1, "level": "beginner"}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 201
        plan = resp.json()
        assert plan["target_duration_sec"] == 60
        assert plan["total_actual_duration_sec"] == 60
        assert len(plan["modules"]) >= 2
        for mod in plan["modules"]:
            assert mod["duration_sec"] >= 5, f"Module duration {mod['duration_sec']} < 5s min bound"

    def test_time_budget_exact_upper_bound_180_min(self):
        """180 minutes masterclass produces exactly 10800 seconds and scales module counts."""
        payload = {
            "topic": "Full-Stack Distributed Operating Systems and Concurrency",
            "learner_profile": {"time_budget_min": 180, "level": "advanced"}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 201
        plan = resp.json()
        assert plan["target_duration_sec"] == 180 * 60
        assert plan["total_actual_duration_sec"] == 180 * 60
        assert len(plan["modules"]) >= 10
        for mod in plan["modules"]:
            assert mod["duration_sec"] >= 5

    def test_update_plan_with_invalid_target_duration_sec_returns_422(self):
        """PUT /api/v1/lessons/{plan_id} with target_duration_sec < 60 must return 422."""
        # Create valid plan first
        create_resp = client.post("/api/v1/lessons/plan", json={"topic": "Linear Algebra"})
        assert create_resp.status_code == 201
        plan_id = create_resp.json()["plan_id"]

        # Attempt to update target_duration_sec to 30 or negative
        for invalid_sec in [0, -10, 30, 59]:
            resp = client.put(f"/api/v1/lessons/{plan_id}", json={"target_duration_sec": invalid_sec})
            assert resp.status_code == 422, f"Expected 422 for target_duration_sec={invalid_sec}, got {resp.status_code}"


# =============================================================================
# 2. UNKNOWN / INVALID LEARNER LEVELS & VISUAL TYPES TESTS
# =============================================================================

class TestUnknownAndInvalidTypesResilience:
    """Tests resilience against invalid enum strings, fuzzy inputs, and schema edge cases."""

    def test_learner_level_unknown_strings_fallback_gracefully(self):
        """Arbitrary/unknown learner level strings fallback to beginner without 500 error."""
        weird_levels = ["super_expert", "god_mode", "12345", "UNKNOWN", "random_string", ""]
        for lvl in weird_levels:
            payload = {
                "topic": "Thermodynamics",
                "learner_profile": {"level": lvl, "time_budget_min": 15}
            }
            resp = client.post("/api/v1/lessons/plan", json=payload)
            assert resp.status_code == 201, f"Failed for level='{lvl}': {resp.text}"
            data = resp.json()
            assert data["level"] in ("beginner", "intermediate", "advanced")

    def test_learner_level_synonyms_and_abbreviations(self):
        """Synonyms like 'novice', 'med', 'adv', 'master' map correctly."""
        mappings = [
            ("novice", LearnerLevel.BEGINNER),
            ("beg", LearnerLevel.BEGINNER),
            ("med", LearnerLevel.INTERMEDIATE),
            ("medium", LearnerLevel.INTERMEDIATE),
            ("adv", LearnerLevel.ADVANCED),
            ("master", LearnerLevel.ADVANCED),
            ("expert", LearnerLevel.ADVANCED),
        ]
        for term, expected_enum in mappings:
            prof = LearnerProfile(level=term)
            assert prof.level == expected_enum

    def test_visual_type_unknown_strings_fallback_safely(self):
        """Invalid visual_type strings in VisualSpec fallback to KEY_TAKEAWAYS without crashing."""
        invalid_types = ["hologram_3d", "virtual_reality", "random_type", "null_type"]
        for vt in invalid_types:
            spec = VisualSpec(visual_type=vt, headline="Test Slide")
            assert spec.visual_type == VisualType.KEY_TAKEAWAYS

    def test_visual_type_fuzzy_matching(self):
        """Fuzzy visual types like 'latex_math', 'code_listing', 'mermaid_diag' map correctly."""
        fuzzy_cases = [
            ("latex_math", VisualType.MATH_EQUATION),
            ("equation_steps", VisualType.MATH_EQUATION),
            ("code_listing", VisualType.CODE_SNIPPET),
            ("prog_sample", VisualType.CODE_SNIPPET),
            ("flow_chart", VisualType.DIAGRAM),
            ("mermaid_graph", VisualType.DIAGRAM),
            ("chrono_history", VisualType.TIMELINE),
            ("comparison_grid", VisualType.COMPARISON_TABLE),
        ]
        for fuzzy_str, expected in fuzzy_cases:
            spec = VisualSpec(visual_type=fuzzy_str, headline="Test Slide")
            assert spec.visual_type == expected

    def test_arbitrary_subject_domain_handled_gracefully(self):
        """Passing an unrecognized subject domain does not crash domain detection or plan creation."""
        payload = {
            "topic": "Alien Exobiology and Astrobiology",
            "subject_domain": "exobiology_unknown_domain_999",
            "learner_profile": {"time_budget_min": 15}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["plan_id"] is not None
        assert len(data["modules"]) >= 4


# =============================================================================
# 3. MALFORMED PLAN UPDATE REQUESTS & HTTP STATUS CODES
# =============================================================================

class TestMalformedPlanUpdatesAndErrors:
    """Verifies proper HTTP 400/404/422 status codes and zero uncaught 500 exceptions."""

    def test_create_plan_empty_json_returns_422(self):
        """POST /api/v1/lessons/plan with empty JSON returns 422 (missing source)."""
        resp = client.post("/api/v1/lessons/plan", json={})
        assert resp.status_code == 422
        assert "at least one of" in resp.text.lower() or "field required" in resp.text.lower()

    def test_create_plan_invalid_json_syntax_returns_422(self):
        """POST /api/v1/lessons/plan with non-JSON or invalid data types."""
        resp = client.post(
            "/api/v1/lessons/plan",
            content="NOT_A_JSON_STRING",
            headers={"Content-Type": "application/json"}
        )
        assert resp.status_code == 422

    def test_get_non_existent_plan_returns_404(self):
        """GET /api/v1/lessons/{non_existent_id} returns 404 Not Found."""
        for fake_id in ["plan_does_not_exist", "plan_null", "invalid_123"]:
            resp = client.get(f"/api/v1/lessons/{fake_id}")
            assert resp.status_code == 404
            assert "not found" in resp.json()["detail"].lower()

    def test_update_non_existent_plan_returns_400(self):
        """PUT /api/v1/lessons/{non_existent_id} returns 400 Bad Request."""
        resp = client.put(
            "/api/v1/lessons/plan_totally_fake_id",
            json={"title": "Updated Title"}
        )
        assert resp.status_code == 400
        assert "not found" in resp.json()["detail"].lower()

    def test_update_plan_reorder_with_foreign_segment_id_returns_400(self):
        """PUT with reorder_segment_ids containing a segment not in the plan returns 400."""
        # Create plan
        create_resp = client.post("/api/v1/lessons/plan", json={"topic": "Optics and Light"})
        assert create_resp.status_code == 201
        plan_id = create_resp.json()["plan_id"]

        resp = client.put(
            f"/api/v1/lessons/{plan_id}",
            json={"reorder_segment_ids": ["seg_foreign_id_that_does_not_exist"]}
        )
        assert resp.status_code == 400
        assert "does not belong" in resp.json()["detail"]

    def test_update_plan_with_negative_segment_duration_returns_422(self):
        """PUT with a segment whose duration_sec < 5 returns 422 Unprocessable Entity."""
        create_resp = client.post("/api/v1/lessons/plan", json={"topic": "Optics"})
        assert create_resp.status_code == 201
        plan = create_resp.json()
        plan_id = plan["plan_id"]

        # Mutate first module duration to negative or 0
        modules = plan["modules"]
        modules[0]["duration_sec"] = -10
        resp = client.put(f"/api/v1/lessons/{plan_id}", json={"modules": modules})
        assert resp.status_code == 422

        # Mutate to 2 (below 5s minimum bound)
        modules[0]["duration_sec"] = 2
        resp = client.put(f"/api/v1/lessons/{plan_id}", json={"modules": modules})
        assert resp.status_code == 422

    def test_update_plan_with_empty_module_title_or_script_returns_422(self):
        """PUT with missing required fields in modules returns 422."""
        create_resp = client.post("/api/v1/lessons/plan", json={"topic": "Optics"})
        plan_id = create_resp.json()["plan_id"]

        malformed_modules = [{
            "segment_id": "seg_001",
            "order": 1,
            # Missing title, duration_sec, script
        }]
        resp = client.put(f"/api/v1/lessons/{plan_id}", json={"modules": malformed_modules})
        assert resp.status_code == 422

    def test_update_plan_with_empty_body_succeeds(self):
        """PUT with empty update payload `{}` should return 200 without changing modules."""
        create_resp = client.post("/api/v1/lessons/plan", json={"topic": "Optics"})
        plan = create_resp.json()
        plan_id = plan["plan_id"]

        resp = client.put(f"/api/v1/lessons/{plan_id}", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan_id"] == plan_id
        assert len(data["modules"]) == len(plan["modules"])


# =============================================================================
# 4. DEVANAGARI HINDI & MULTILINGUAL / SPECIAL UNICODE RESILIENCE
# =============================================================================

class TestUnicodeAndDevanagariResilience:
    """Tests Devanagari Hindi, mathematical symbols, emojis, and RTL/CJK unicode robustness."""

    def test_hindi_devanagari_full_lesson_plan_generation_and_persistence(self):
        """
        Generates a lesson plan with Devanagari Hindi topic, goals, weak concepts,
        and verifies script narration in Hindi and disk persistence reload.
        """
        payload = {
            "topic": "क्वांटम यांत्रिकी और श्रोडिंगर समीकरण (Schrödinger Equation)",
            "subject_domain": "physics",
            "learner_profile": {
                "student_id": "छात्र_१०१",
                "level": "intermediate",
                "language": "hi",
                "time_budget_min": 15,
                "prior_knowledge": "कक्षा १२वीं भौतिकी और अवकलन",
                "learning_goal": r"तरंग फलन \Psi(x,t) और संभाव्यता घनत्व को समझना",
                "weak_concepts": ["सम्मिश्र संख्याएँ (Complex Numbers)", "आंशिक अवकलन (Partial Derivatives)"]
            },
            "custom_instructions": "कृपया उदाहरण सरल और हिंदी में समझाएं।"
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 201, f"Hindi plan generation failed: {resp.text}"
        data = resp.json()

        assert data["language"] == "hi"
        assert len(data["prerequisite_refreshers"]) == 2
        assert "सम्मिश्र संख्याएँ (Complex Numbers)" in data["prerequisite_refreshers"]

        # Intro script should contain Hindi greeting
        intro_script = data["modules"][0]["script"]
        assert "नमस्ते" in intro_script
        assert "सम्मिश्र संख्याएँ" in intro_script

        # Checkpoints in Hindi
        chk_mods = [m for m in data["modules"] if m.get("checkpoint_question")]
        assert len(chk_mods) >= 1
        assert any("क्या" in m["checkpoint_question"]["question_text"] or "?" in m["checkpoint_question"]["question_text"] for m in chk_mods)

        # Verify disk persistence reload
        fresh_service = PlannerService()
        reloaded = fresh_service.get_plan(data["plan_id"])
        assert reloaded is not None
        assert reloaded.language == "hi"
        assert "नमस्ते" in reloaded.modules[0].script

    def test_special_mathematical_unicode_and_latex_symbols(self):
        """Verifies special mathematical unicode characters in topic and scripts."""
        complex_topic = "Multivariable Calculus: ∮_C (P dx + Q dy) = ∬_R (∂Q/∂x - ∂P/∂y) dA & ∇ × E = -∂B/∂t"
        payload = {
            "topic": complex_topic,
            "learner_profile": {"time_budget_min": 15, "level": "advanced"}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["subject_domain"] == "math"
        assert len(data["modules"]) >= 4

    def test_emojis_and_multilingual_unicode_scripts(self):
        """Ensures emojis and diverse scripts (Japanese, Arabic, Cyrillic, Accented Latin) don't crash."""
        diverse_topic = "🚀 AI & Deep Learning 🧠: 日本語 (機械学習) / العربية (تعلم الآلة) / Русский / Café Müller"
        payload = {
            "topic": diverse_topic,
            "learner_profile": {"time_budget_min": 15}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["plan_id"] is not None

    def test_zero_width_and_control_unicode_characters(self):
        """Zero-width spaces and formatting markers in topic string."""
        zw_topic = "Introduction\u200bto\u200cQuantum\u200dComputing\ufeff"
        payload = {
            "topic": zw_topic,
            "learner_profile": {"time_budget_min": 15}
        }
        resp = client.post("/api/v1/lessons/plan", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["plan_id"] is not None


# =============================================================================
# 5. CONCURRENCY & EXTREME LOAD TESTS
# =============================================================================

class TestConcurrencyAndStress:
    """Stress tests rapid consecutive creations and listing integrity."""

    def test_rapid_consecutive_plan_creations(self):
        """Generates 10 plans rapidly in succession across diverse topics and domains."""
        topics = [
            ("Math: Integration by Parts", "math", "beginner", 5),
            ("CS: Dijkstra Shortest Path", "computer_science", "advanced", 15),
            ("Bio: Cellular Mitosis and Cytokinesis", "biology", "intermediate", 30),
            ("Hist: Roman Empire Transition to Republic", "history", "beginner", 15),
            ("Physics: Quantum Superposition", "physics", "advanced", 60),
            ("CS: Binary Search Trees", "computer_science", "beginner", 5),
            ("Math: Eigenvalues and Linear Transformations", "math", "advanced", 30),
            ("Bio: DNA Replication Forks", "biology", "intermediate", 15),
            ("Hist: Industrial Revolution Steam Power", "history", "intermediate", 15),
            ("General: Cognitive Psychology Memory Models", "general", "beginner", 15),
        ]
        created_ids = []
        for topic_name, domain, level, time_min in topics:
            resp = client.post(
                "/api/v1/lessons/plan",
                json={
                    "topic": topic_name,
                    "subject_domain": domain,
                    "learner_profile": {
                        "level": level,
                        "time_budget_min": time_min
                    }
                }
            )
            assert resp.status_code == 201, f"Failed on topic {topic_name}: {resp.text}"
            data = resp.json()
            created_ids.append(data["plan_id"])
            assert data["target_duration_sec"] == time_min * 60
            assert data["total_actual_duration_sec"] == time_min * 60

        # Verify all created plans appear in list endpoint
        list_resp = client.get("/api/v1/lessons")
        assert list_resp.status_code == 200
        all_summaries = list_resp.json()
        summary_ids = {s["plan_id"] for s in all_summaries}
        for cid in created_ids:
            assert cid in summary_ids, f"Plan {cid} missing from list summaries"
