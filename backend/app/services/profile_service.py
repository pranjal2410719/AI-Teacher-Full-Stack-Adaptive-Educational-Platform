"""
AI Teacher - Student Learning Profile & Recommendation Service.
Maintains persistent student profiles, cross-session mastery tracking, weak concept maps,
and computes personalized study roadmaps and next-topic recommendations.
"""

import os
import json
import logging
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from backend.app.config import settings
from backend.app.models.profile import (
    StudentProfile,
    StudentProfileUpdateRequest,
    TopicRecommendation,
)

logger = logging.getLogger("ai_teacher.profile")

PROFILE_STORAGE_DIR = os.path.join(settings.data_dir, "profiles")
SQLITE_DB_PATH = os.path.join(settings.data_dir, "student_profiles.db")
os.makedirs(PROFILE_STORAGE_DIR, exist_ok=True)


class ProfileService:
    """
    Persistent student profile store with SQLite & JSON dual persistence,
    tracking cross-session mastery analytics and generating adaptive next-step recommendations.
    """

    def __init__(self):
        self._profiles: Dict[str, StudentProfile] = {}
        self._init_sqlite()
        self._load_persisted_profiles()

    def _init_sqlite(self):
        """Initializes SQLite tables for persistent student profiles."""
        try:
            with sqlite3.connect(SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_profiles (
                        student_id TEXT PRIMARY KEY,
                        name TEXT,
                        preferred_language TEXT,
                        preferred_level TEXT,
                        total_lessons_completed INTEGER,
                        average_mastery_percent REAL,
                        total_time_spent_min INTEGER,
                        profile_json TEXT,
                        updated_at TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to initialize SQLite profiles DB: {e}")

    def _load_persisted_profiles(self):
        """Loads profiles from SQLite or JSON fallback."""
        # 1. Try SQLite
        try:
            with sqlite3.connect(SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT student_id, profile_json FROM student_profiles")
                rows = cursor.fetchall()
                for student_id, profile_json in rows:
                    data = json.loads(profile_json)
                    self._profiles[student_id] = StudentProfile(**data)
        except Exception as e:
            logger.warning(f"Error reading SQLite profiles: {e}")

        # 2. Try JSON directory fallback
        try:
            for fname in os.listdir(PROFILE_STORAGE_DIR):
                if fname.endswith(".json"):
                    with open(os.path.join(PROFILE_STORAGE_DIR, fname), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        prof = StudentProfile(**data)
                        self._profiles[prof.student_id] = prof
        except Exception as e:
            logger.warning(f"Error loading JSON profiles fallback: {e}")

    def _save_profile(self, profile: StudentProfile):
        """Persists profile to both SQLite and JSON."""
        self._profiles[profile.student_id] = profile
        profile_json = json.dumps(profile.model_dump(), indent=2)

        # JSON file save
        try:
            fpath = os.path.join(PROFILE_STORAGE_DIR, f"{profile.student_id}.json")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(profile_json)
        except Exception as e:
            logger.warning(f"Failed to write JSON profile for {profile.student_id}: {e}")

        # SQLite save
        try:
            with sqlite3.connect(SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO student_profiles
                    (student_id, name, preferred_language, preferred_level, total_lessons_completed, average_mastery_percent, total_time_spent_min, profile_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.student_id,
                    profile.name,
                    profile.preferred_language,
                    profile.preferred_level,
                    profile.total_lessons_completed,
                    profile.average_mastery_percent,
                    profile.total_time_spent_min,
                    profile_json,
                    profile.updated_at
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to write SQLite profile for {profile.student_id}: {e}")

    # -------------------------------------------------------------------------
    # Profile Retrieval & Management
    # -------------------------------------------------------------------------
    def get_profile(self, student_id: str) -> StudentProfile:
        """Retrieves an existing student profile or creates a default guest record."""
        if student_id in self._profiles:
            return self._profiles[student_id]

        # Initialize fresh learner profile
        profile = StudentProfile(
            student_id=student_id,
            name="Learner",
            preferred_language="en",
            preferred_level="intermediate",
            total_lessons_completed=0,
            average_mastery_percent=0.0,
            mastery_by_subject={},
            concept_mastery={},
            known_weak_areas=[],
            weak_areas=[],
            learning_history=[],
            completed_lessons=[],
            total_time_spent_min=0,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        self._save_profile(profile)
        return profile

    def update_profile(self, student_id: str, req: StudentProfileUpdateRequest) -> StudentProfile:
        """Updates user preferences and settings."""
        profile = self.get_profile(student_id)
        if req.name is not None:
            profile.name = req.name
        if req.preferred_language is not None:
            profile.preferred_language = req.preferred_language
        if req.preferred_level is not None:
            profile.preferred_level = req.preferred_level
        if req.known_weak_areas is not None:
            profile.known_weak_areas = req.known_weak_areas
            profile.weak_areas = req.known_weak_areas

        profile.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_profile(profile)
        return profile

    def record_lesson_completion(
        self,
        student_id: str,
        lesson_id: str,
        score_percent: float,
        strong_concepts: List[str],
        weak_concepts: List[str]
    ) -> StudentProfile:
        """
        Updates persistent student profile upon completing an assessment.
        """
        profile = self.get_profile(student_id)

        # Update lesson counters
        profile.total_lessons_completed += 1
        if lesson_id not in profile.completed_lessons:
            profile.completed_lessons.append(lesson_id)
        profile.total_time_spent_min += 15

        # Update average mastery
        prev_avg = profile.average_mastery_percent
        n = profile.total_lessons_completed
        profile.average_mastery_percent = round(((prev_avg * (n - 1)) + score_percent) / n, 1)

        # Update concept mastery scores
        for sc in strong_concepts:
            profile.concept_mastery[sc] = max(profile.concept_mastery.get(sc, 0.0), score_percent / 100.0)
            if sc in profile.known_weak_areas:
                profile.known_weak_areas.remove(sc)
            if sc in profile.weak_areas:
                profile.weak_areas.remove(sc)

        for wc in weak_concepts:
            if wc not in profile.known_weak_areas:
                profile.known_weak_areas.append(wc)
            if wc not in profile.weak_areas:
                profile.weak_areas.append(wc)
            profile.concept_mastery[wc] = min(profile.concept_mastery.get(wc, 1.0), score_percent / 100.0)

        # Append to learning history
        profile.learning_history.append({
            "lesson_id": lesson_id,
            "score": score_percent,
            "strong_concepts": strong_concepts,
            "weak_concepts": weak_concepts,
            "date": datetime.now(timezone.utc).isoformat()
        })

        profile.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_profile(profile)
        return profile

    # -------------------------------------------------------------------------
    # Recommendation Engine
    # -------------------------------------------------------------------------
    def get_recommendations(self, student_id: str) -> List[TopicRecommendation]:
        """
        Synthesizes personalized learning recommendations based on mastery history and weak concepts.
        """
        profile = self.get_profile(student_id)
        recommendations = []

        # 1. Prerequisite Refreshers for Weak Areas
        if profile.known_weak_areas:
            for weak_concept in profile.known_weak_areas[:2]:
                recommendations.append(TopicRecommendation(
                    topic=f"Foundational Refresher: {weak_concept}",
                    level=profile.preferred_level,
                    rationale=f"Reinforce conceptual foundation based on your diagnostic feedback in '{weak_concept}'.",
                    prerequisite_concepts=[weak_concept]
                ))

        # 2. Next-Topic Progression
        if "Calculus" in str(profile.completed_lessons) or any("limit" in str(h) for h in profile.learning_history) or not profile.completed_lessons:
            recommendations.append(TopicRecommendation(
                topic="Product and Quotient Rules in Calculus",
                level="intermediate",
                rationale="Natural extension of limits and derivative definitions.",
                prerequisite_concepts=["Foundational Limits", "Derivative Definition"]
            ))
            recommendations.append(TopicRecommendation(
                topic="Chain Rule for Composite Functions",
                level="intermediate",
                rationale="Master derivative composition for multi-layered mathematical models.",
                prerequisite_concepts=["Power Rule", "Function Composition"]
            ))

        if any("bst" in str(h) or "tree" in str(h) for h in profile.learning_history):
            recommendations.append(TopicRecommendation(
                topic="Self-Balancing AVL Trees & Rotations",
                level="intermediate",
                rationale="Prevent worst-case O(n) degradation through dynamic height balancing.",
                prerequisite_concepts=["Binary Search Trees"]
            ))

        return recommendations


# Global singleton instance
profile_service = ProfileService()
