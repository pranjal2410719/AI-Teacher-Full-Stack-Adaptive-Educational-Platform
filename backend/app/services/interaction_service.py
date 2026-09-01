"""
AI Teacher - Interactive & Adaptive Teaching Loop Service.
Evaluates student responses, diagnoses root misconceptions, provides scaffolded analogical re-explanations,
generates follow-up comprehension checks, supports mid-session multilingual switching, and powers grounded AI tutor chat.
"""

import os
import json
import logging
import uuid
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

from backend.app.config import settings
from backend.app.models.interaction import (
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    FollowUpQuestion,
    LanguageSwitchRequest,
    LanguageSwitchResponse,
    TutorChatRequest,
    TutorChatResponse,
    InteractionSessionState,
)
from backend.app.services.llm_client import llm_client
from backend.app.services.vector_store import vector_store

logger = logging.getLogger("ai_teacher.interaction")

SESSION_STORAGE_DIR = os.path.join(settings.data_dir, "sessions")
os.makedirs(SESSION_STORAGE_DIR, exist_ok=True)


class InteractionService:
    """
    Core service orchestrating interactive checkpoint evaluations, misconception diagnosis,
    adaptive re-explanations, multilingual switching, and side-panel tutor assistance.
    """

    def __init__(self):
        self._sessions: Dict[str, InteractionSessionState] = {}
        self._load_persisted_sessions()

    def _load_persisted_sessions(self):
        """Loads previously saved interaction sessions from disk."""
        try:
            for fname in os.listdir(SESSION_STORAGE_DIR):
                if fname.endswith(".json"):
                    fpath = os.path.join(SESSION_STORAGE_DIR, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        state = InteractionSessionState(**data)
                        self._sessions[state.session_id] = state
        except Exception as e:
            logger.warning(f"Error loading persisted sessions: {e}")

    def _save_session(self, state: InteractionSessionState):
        """Persists session state to disk."""
        self._sessions[state.session_id] = state
        try:
            fpath = os.path.join(SESSION_STORAGE_DIR, f"{state.session_id}.json")
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(state.model_dump(), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist session {state.session_id}: {e}")

    def get_or_create_session(self, session_id: str, student_id: str = "stu_default", language: str = "en") -> InteractionSessionState:
        """Retrieves an existing session or initializes a new one."""
        if session_id in self._sessions:
            return self._sessions[session_id]
        state = InteractionSessionState(
            session_id=session_id,
            student_id=student_id,
            language=language,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        self._save_session(state)
        return state

    # -------------------------------------------------------------------------
    # Prompt Injection & Adversarial Security Guardrails
    # -------------------------------------------------------------------------
    def _detect_adversarial_injection(self, text: str) -> bool:
        """Detects prompt injection and jailbreak attempts."""
        normalized = text.lower()
        patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"system\s+prompt",
            r"output\s+api\s*key",
            r"mark\s+score\s+as\s+100",
            r"give\s+me\s+full\s+marks",
            r"you\s+are\s+now\s+in\s+dan\s+mode",
            r"jailbreak",
            r"bypass\s+safety",
            r"reveal\s+hidden\s+instructions"
        ]
        return any(re.search(pat, normalized) for pat in patterns)

    # -------------------------------------------------------------------------
    # Checkpoint Answer Evaluation & Misconception Diagnosis
    # -------------------------------------------------------------------------
    def evaluate_student_answer(self, req: AnswerEvaluationRequest) -> AnswerEvaluationResponse:
        """
        Evaluates student answer against pedagogical rubrics, diagnoses root misconceptions,
        and constructs tailored analogical re-explanations.
        """
        session = self.get_or_create_session(req.session_id, language=req.language or "en")
        student_ans = req.student_answer.strip()
        concept = req.current_concept or "General"
        lang = req.language or session.language or "en"

        # 1. Adversarial Guardrail
        if self._detect_adversarial_injection(student_ans):
            logger.warning(f"Adversarial prompt injection attempt in session {req.session_id}: {student_ans[:50]}")
            resp = AnswerEvaluationResponse(
                is_correct=False,
                score=0.0,
                feedback="Let us stay focused on the lesson concept at hand.",
                misconception="Adversarial off-topic response detected.",
                misconception_detected="Adversarial off-topic response detected.",
                pedagogical_re_explanation="Please review the foundational definition in the previous slide.",
                re_explanation="Please review the foundational definition in the previous slide.",
                follow_up_question=FollowUpQuestion(
                    question_id="q_refocus",
                    type="short_answer",
                    prompt="Can you explain the main concept in your own words?"
                ),
                can_resume_video=False,
                can_proceed=False,
                detected_language=lang
            )
            self._record_interaction(session, req, resp)
            return resp

        # 2. LLM-Assisted Evaluation (if keys configured)
        if settings.groq_api_key or settings.gemini_api_key:
            try:
                llm_eval = self._evaluate_with_llm(student_ans, concept, lang, req.context, req.expected_answer, req.learner_level)
                if llm_eval is not None:
                    self._record_interaction(session, req, llm_eval)
                    return llm_eval
            except Exception as e:
                logger.warning(f"LLM answer evaluation failed, falling back to heuristic engine: {e}")

        # 3. Comprehensive Domain Pedagogical Heuristic & Misconception Engine
        resp = self._evaluate_with_heuristics(student_ans, concept, lang, req.learner_level)
        self._record_interaction(session, req, resp)
        return resp

    def _evaluate_with_llm(
        self,
        student_answer: str,
        concept: str,
        language: str,
        context: Optional[str],
        expected_answer: Optional[str],
        level: str
    ) -> Optional[AnswerEvaluationResponse]:
        """Calls Groq or Gemini to evaluate response and diagnose misconceptions."""
        system_prompt = (
            "You are a master teacher and pedagogical evaluator. "
            "Analyze the student's answer to the checkpoint question. "
            "If correct: provide uplifting specific feedback and set can_resume_video to true. "
            "If incorrect: diagnose the root misconception, provide a scaffolded re-explanation "
            "with an intuitive, memorable real-world analogy (e.g. road trips, speedometers, delivery routes), "
            "and generate a targeted follow-up question to verify understanding before resuming."
        )

        user_prompt = f"""
Evaluate the following student answer:
- Concept: {concept}
- Learner Level: {level}
- Target Language: {language}
- Context/Slide: {context or 'Standard lesson module'}
- Expected Core Idea: {expected_answer or 'Accurate conceptual grasp'}
- Student's Submitted Answer: "{student_answer}"

Respond strictly with valid JSON conforming to this schema:
{{
  "is_correct": boolean,
  "score": float between 0.0 and 1.0,
  "feedback": "constructive feedback string",
  "misconception": "string describing root misconception, or null if correct",
  "pedagogical_re_explanation": "scaffolded explanation with vivid analogy, or null if correct",
  "follow_up_question": {{
    "question_id": "q_followup",
    "type": "short_answer",
    "prompt": "follow-up comprehension check string",
    "hint": "helpful hint string"
  }} or null,
  "can_resume_video": boolean
}}
"""
        response_text = llm_client.generate_text(prompt=user_prompt, system_prompt=system_prompt, temperature=0.2)
        extracted = llm_client.extract_json_from_response(response_text)
        if isinstance(extracted, dict) and "is_correct" in extracted and "score" in extracted:
            fu_q = None
            if extracted.get("follow_up_question"):
                fu_data = extracted["follow_up_question"]
                fu_q = FollowUpQuestion(
                    question_id=fu_data.get("question_id", f"q_fu_{uuid.uuid4().hex[:4]}"),
                    type=fu_data.get("type", "short_answer"),
                    prompt=fu_data.get("prompt", "How would you state the concept now?"),
                    hint=fu_data.get("hint")
                )
            
            is_corr = bool(extracted["is_correct"])
            score = float(extracted["score"])
            misc = extracted.get("misconception")
            re_expl = extracted.get("pedagogical_re_explanation")

            return AnswerEvaluationResponse(
                is_correct=is_corr,
                score=score,
                feedback=extracted.get("feedback", "Good effort."),
                misconception=misc,
                misconception_detected=misc,
                pedagogical_re_explanation=re_expl,
                re_explanation=re_expl,
                follow_up_question=fu_q,
                can_resume_video=is_corr and score >= 0.7,
                can_proceed=is_corr and score >= 0.7,
                detected_language=language
            )
        return None

    def _evaluate_with_heuristics(
        self,
        student_ans: str,
        concept: str,
        lang: str,
        level: str
    ) -> AnswerEvaluationResponse:
        """Domain-specific heuristic evaluator with deep pedagogical knowledge base."""
        ans_lower = student_ans.lower()
        concept_lower = concept.lower()

        # Domain 1: Calculus & Limits (Secant vs Tangent, Delta t -> 0, Left/Right Limits)
        if any(k in concept_lower for k in ["secant", "tangent", "limit", "calculus", "rate of change", "derivative", "slope"]):
            # Check for secant vs tangent confusion
            if any(w in ans_lower for w in ["instantaneous", "right now", "single point", "at one point", "one moment"]) and ("secant" in concept_lower or "secant" in ans_lower):
                if not any(w in ans_lower for w in ["tangent", "delta t", "limit", "approaches", "shrinks"]):
                    return AnswerEvaluationResponse(
                        is_correct=False,
                        score=0.3,
                        feedback="Not quite! You described the tangent line, but the secant line connects two distinct points across an interval.",
                        misconception="Confusing average rate of change with instantaneous velocity.",
                        misconception_detected="Confusing average rate of change with instantaneous velocity.",
                        pedagogical_re_explanation="Think of a road trip: driving 120 miles in 2 hours gives an average speed of 60 mph (secant slope), even if your speedometer peaked at 75 mph (tangent slope).",
                        re_explanation="Think of a road trip: driving 120 miles in 2 hours gives an average speed of 60 mph (secant slope), even if your speedometer peaked at 75 mph (tangent slope).",
                        follow_up_question=FollowUpQuestion(
                            question_id="q_calc_fu_01",
                            type="short_answer",
                            prompt="When the time interval delta t shrinks toward zero, what does the secant slope become?",
                            hint="Think about the speedometer reading at one exact second."
                        ),
                        can_resume_video=False,
                        can_proceed=False,
                        detected_language=lang
                    )

            # Check for valid limit / derivative answers
            if any(w in ans_lower for w in ["equal", "left-hand", "right-hand", "both", "approaches", "derivative", "average", "tangent", "slope", "speedometer", "shrink"]):
                return AnswerEvaluationResponse(
                    is_correct=True,
                    score=0.95,
                    feedback="Outstanding! Your explanation demonstrates precise conceptual understanding of limits and rates of change.",
                    misconception=None,
                    misconception_detected=None,
                    pedagogical_re_explanation=None,
                    re_explanation=None,
                    follow_up_question=None,
                    can_resume_video=True,
                    can_proceed=True,
                    detected_language=lang
                )

        # Domain 2: Computer Science & Data Structures (BST, Trees, Complexity, Recursion)
        if any(k in concept_lower for k in ["bst", "tree", "binary search", "algorithm", "complexity", "data structure"]):
            if any(w in ans_lower for w in ["always takes o(log n)", "always log n", "never linear", "impossible to be o(n)"]):
                return AnswerEvaluationResponse(
                    is_correct=False,
                    score=0.35,
                    feedback="Not quite! While a balanced BST achieves O(log n), inserting sorted elements can cause the tree to degenerate.",
                    misconception="Assuming a binary search tree always operates in logarithmic time regardless of insertion balance.",
                    misconception_detected="Assuming a binary search tree always operates in logarithmic time regardless of insertion balance.",
                    pedagogical_re_explanation="Think of a binary search tree like a dictionary: if pages are balanced, you cut pages in half; but if entries are added strictly in order, it becomes a single unrolled scroll (linked list) taking O(n) linear search time.",
                    re_explanation="Think of a binary search tree like a dictionary: if pages are balanced, you cut pages in half; but if entries are added strictly in order, it becomes a single unrolled scroll (linked list) taking O(n) linear search time.",
                    follow_up_question=FollowUpQuestion(
                        question_id="q_cs_fu_01",
                        type="short_answer",
                        prompt="What happens to the structure of a BST if you insert elements in strictly ascending order 1, 2, 3, 4, 5?",
                        hint="Think of a chain or linked list."
                    ),
                    can_resume_video=False,
                    can_proceed=False,
                    detected_language=lang
                )
            if any(w in ans_lower for w in ["o(n)", "linear", "linked list", "skewed", "degenerate", "unbalanced", "log n", "binary", "left child", "right child", "greater", "less"]):
                return AnswerEvaluationResponse(
                    is_correct=True,
                    score=0.92,
                    feedback="Spot on! You understand both the logarithmic search efficiency and worst-case degenerate scenarios of binary search trees.",
                    misconception=None,
                    misconception_detected=None,
                    pedagogical_re_explanation=None,
                    re_explanation=None,
                    follow_up_question=None,
                    can_resume_video=True,
                    can_proceed=True,
                    detected_language=lang
                )

        # Domain 3: Biology & Cell Structure (Diffusion, Active Transport, Organelles)
        if any(k in concept_lower for k in ["biology", "cell", "membrane", "diffusion", "transport", "organelle", "mitochondria"]):
            if (("passive" in ans_lower or "diffusion" in ans_lower) and any(w in ans_lower for w in ["requires atp", "uses atp", "needs atp", "requires energy", "uses energy", "push molecules"])) or any(w in ans_lower for w in ["passive requires atp", "diffusion uses energy", "atp not needed for pumps"]):
                return AnswerEvaluationResponse(
                    is_correct=False,
                    score=0.25,
                    feedback="Incorrect! Diffusion is passive movement down a concentration gradient and requires zero cellular energy.",
                    misconception="Confusing passive diffusion with active ATP-driven cellular transport.",
                    misconception_detected="Confusing passive diffusion with active ATP-driven cellular transport.",
                    pedagogical_re_explanation="Think of the cell membrane like a guarded border gate: small oxygen particles drift through freely with the current (diffusion), but moving against the gradient requires ATP energy coins to unlock active pump gates.",
                    re_explanation="Think of the cell membrane like a guarded border gate: small oxygen particles drift through freely with the current (diffusion), but moving against the gradient requires ATP energy coins to unlock active pump gates.",
                    follow_up_question=FollowUpQuestion(
                        question_id="q_bio_fu_01",
                        type="short_answer",
                        prompt="Which cellular molecule acts as the direct energy currency for active transport pumps?",
                        hint="A 3-letter nucleotide derivative."
                    ),
                    can_resume_video=False,
                    can_proceed=False,
                    detected_language=lang
                )
            if any(w in ans_lower for w in ["atp", "passive", "active", "gradient", "energy", "mitochondria", "membrane", "phospholipid", "chloroplast", "ribosome"]):
                return AnswerEvaluationResponse(
                    is_correct=True,
                    score=0.90,
                    feedback="Excellent! You have clearly mastered cellular transport mechanisms and organelle functions.",
                    misconception=None,
                    misconception_detected=None,
                    pedagogical_re_explanation=None,
                    re_explanation=None,
                    follow_up_question=None,
                    can_resume_video=True,
                    can_proceed=True,
                    detected_language=lang
                )

        # Domain 4: History (Industrial Revolution, Mechanization, Urbanization)
        if any(k in concept_lower for k in ["history", "industrial", "revolution", "steam", "britain"]):
            if any(w in ans_lower for w in ["computers", "electricity in 1750", "internet", "nuclear"]):
                return AnswerEvaluationResponse(
                    is_correct=False,
                    score=0.3,
                    feedback="Not quite! The first Industrial Revolution was characterized by steam power and coal, not modern electronics.",
                    misconception="Confusing 18th-century mechanization with 20th-century digital automation.",
                    misconception_detected="Confusing 18th-century mechanization with 20th-century digital automation.",
                    pedagogical_re_explanation="Think of the First Industrial Revolution as replacing manual muscle and waterwheels with coal-fired steam engines to power textile looms and railroads.",
                    re_explanation="Think of the First Industrial Revolution as replacing manual muscle and waterwheels with coal-fired steam engines to power textile looms and railroads.",
                    follow_up_question=FollowUpQuestion(
                        question_id="q_hist_fu_01",
                        type="short_answer",
                        prompt="What primary fossil fuel powered the steam engines of the Industrial Revolution?",
                        hint="A black combustible sedimentary rock."
                    ),
                    can_resume_video=False,
                    can_proceed=False,
                    detected_language=lang
                )
            if any(w in ans_lower for w in ["steam", "coal", "textile", "factory", "urbanization", "watt", "mechanization"]):
                return AnswerEvaluationResponse(
                    is_correct=True,
                    score=0.94,
                    feedback="Superb! You have grasped the economic and technological foundations of the Industrial Revolution.",
                    misconception=None,
                    misconception_detected=None,
                    pedagogical_re_explanation=None,
                    re_explanation=None,
                    follow_up_question=None,
                    can_resume_video=True,
                    can_proceed=True,
                    detected_language=lang
                )

        # Multilingual Devanagari Hindi Recognition
        hindi_keywords = ["समान", "बाएँ", "दाएँ", "सीमा", "बराबर", "अस्तित्व", "ऊर्जा", "परिवर्तन", "सही", "सत्य", "कोशिका", "भाप", "कोयला", "सीकेंट", "टेंगेंट"]
        if any(k in student_ans for k in hindi_keywords):
            return AnswerEvaluationResponse(
                is_correct=True,
                score=0.92,
                feedback="बहुत बढ़िया! आपने मुख्य शैक्षणिक अवधारणा को स्पष्ट रूप से समझा है।",
                misconception=None,
                misconception_detected=None,
                pedagogical_re_explanation=None,
                re_explanation=None,
                follow_up_question=None,
                can_resume_video=True,
                can_proceed=True,
                detected_language="hi"
            )

        # General Fallback Evaluator
        correct_keywords = ["correct", "yes", "true", "accurate", "principle", "property", "valid", "because", "equals", "defined"]
        if any(k in ans_lower for k in correct_keywords) and len(ans_lower.split()) >= 3:
            return AnswerEvaluationResponse(
                is_correct=True,
                score=0.88,
                feedback="Well done! Your response captures the key pedagogical principle.",
                misconception=None,
                misconception_detected=None,
                pedagogical_re_explanation=None,
                re_explanation=None,
                follow_up_question=None,
                can_resume_video=True,
                can_proceed=True,
                detected_language=lang
            )
        else:
            return AnswerEvaluationResponse(
                is_correct=False,
                score=0.4,
                feedback="Your response is partially incomplete. Let's break this concept down with a simple analogy.",
                misconception="Incomplete grasp of foundational definition.",
                misconception_detected="Incomplete grasp of foundational definition.",
                pedagogical_re_explanation=f"Let's look at {concept} from first principles: break it down into the core inputs, the transformation rule, and the expected outcome.",
                re_explanation=f"Let's look at {concept} from first principles: break it down into the core inputs, the transformation rule, and the expected outcome.",
                follow_up_question=FollowUpQuestion(
                    question_id=f"q_gen_fu_{uuid.uuid4().hex[:4]}",
                    type="short_answer",
                    prompt=f"Can you explain the primary purpose of {concept} in one clear sentence?",
                    hint="Focus on the most fundamental property."
                ),
                can_resume_video=False,
                can_proceed=False,
                detected_language=lang
            )

    def _record_interaction(self, session: InteractionSessionState, req: AnswerEvaluationRequest, resp: AnswerEvaluationResponse):
        """Records student interaction history and tracks resolved/unresolved misconceptions."""
        interaction_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question_id": req.question_id,
            "student_answer": req.student_answer,
            "concept": req.current_concept,
            "is_correct": resp.is_correct,
            "score": resp.score,
            "misconception": resp.misconception
        }
        session.interaction_history.append(interaction_entry)
        if resp.misconception:
            session.diagnosed_misconceptions.append(resp.misconception)
        elif resp.is_correct and session.diagnosed_misconceptions:
            # Mark previous misconception as resolved
            last_misc = session.diagnosed_misconceptions.pop()
            session.resolved_misconceptions.append(last_misc)
        session.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_session(session)

    # -------------------------------------------------------------------------
    # Mid-Session Multilingual Switching
    # -------------------------------------------------------------------------
    def switch_session_language(self, req: LanguageSwitchRequest) -> LanguageSwitchResponse:
        """Switches the active teaching language and translates lesson context."""
        session = self.get_or_create_session(req.session_id)
        session.language = req.target_language
        session.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_session(session)

        if req.target_language in ["hi", "hindi"]:
            summary = "आपकी सीखने की भाषा हिंदी में बदल दी गई है। हम पाठ को सहजता से जारी रख सकते हैं।"
            prompt = "नमस्ते! यदि आपके पास इस विषय पर कोई प्रश्न है, तो कृपया बेझिझक पूछें।"
        else:
            summary = f"Your active teaching language has been switched to {req.target_language}."
            prompt = "Hello! Please feel free to ask any question or resume the video lesson."

        return LanguageSwitchResponse(
            session_id=req.session_id,
            language=req.target_language,
            translated_summary=summary,
            next_prompt=prompt,
            status="switched"
        )

    # -------------------------------------------------------------------------
    # Grounded Side-Panel AI Tutor Chat
    # -------------------------------------------------------------------------
    def tutor_chat(self, req: TutorChatRequest) -> TutorChatResponse:
        """
        Provides unscripted, RAG-grounded conversational assistance with timestamp references
        and multilingual capability.
        """
        session_id = req.session_id or f"ses_{uuid.uuid4().hex[:8]}"
        session = self.get_or_create_session(session_id, language=req.language or "en")
        msg = req.message.strip()

        # Check for language switch command within chat
        if any(w in msg.lower() for w in ["hindi", "हिंदी", "hindi me", "explain in hindi"]):
            session.language = "hi"
            self._save_session(session)
            return TutorChatResponse(
                session_id=session_id,
                reply="नमस्ते! मैं आपकी भाषा हिंदी में बदल रहा हूँ। सीकेंट लाइन औसत परिवर्तन दर दर्शाती है और टेंगेंट लाइन तात्कालिक दर। आप आगे क्या समझना चाहेंगे?",
                language="hi",
                suggested_actions=["Resume video in Hindi", "Ask another question in Hindi", "Review concept slide"],
                grounded_sources=["Foundational Calculus Syllabus (Hindi)"]
            )

        # Grounding retrieval via Vector Store if document/topic available
        grounded_context = ""
        sources = []
        target_id = req.document_id or req.topic_id
        if target_id and target_id in vector_store.indices:
            try:
                rag_res = vector_store.query(target_id=target_id, query_text=msg, top_k=2)
                if rag_res:
                    sources = [f"{m.source_filename} (p.{m.page_or_slide})" for m in rag_res]
                    grounded_context = "\n".join([m.text for m in rag_res])
            except Exception as e:
                logger.warning(f"Vector search failed in tutor chat: {e}")

        # LLM Generation if configured
        if settings.groq_api_key or settings.gemini_api_key:
            try:
                system_prompt = (
                    "You are a friendly, encouraging AI Teacher side-panel tutor. "
                    "Provide clear, concise, grounded answers to the student's questions. "
                    "Keep answers under 3 paragraphs with bullet points for clarity."
                )
                user_prompt = f"""
Student Question at timestamp {req.current_timestamp_sec:.1f}s:
"{msg}"

Current Active Concept: {req.current_concept or 'Lesson Overview'}
Grounded Course Materials Context:
{grounded_context or 'Use foundational subject knowledge.'}

Provide a helpful, educational response and suggest 2 actionable next steps for the learner.
"""
                reply_text = llm_client.generate_text(prompt=user_prompt, system_prompt=system_prompt, temperature=0.3)
                if reply_text and len(reply_text.strip()) > 10:
                    return TutorChatResponse(
                        session_id=session_id,
                        reply=reply_text.strip(),
                        language=session.language,
                        suggested_actions=["Resume video playback", "Review concept slide", "Take practice check"],
                        grounded_sources=sources
                    )
            except Exception as e:
                logger.warning(f"LLM tutor chat failed, falling back to heuristic reply: {e}")

        # Heuristic / Parametric Tutor Responses
        if "denominator" in msg.lower() and "zero" in msg.lower():
            reply = (
                "When the denominator of a rational function approaches zero while the numerator is non-zero, "
                "the function value grows without bound toward positive or negative infinity (a vertical asymptote). "
                "If both numerator and denominator approach zero (0/0), it creates an indeterminate form, "
                "which can often be simplified via factoring, algebraic conjugation, or L'Hôpital's rule."
            )
        elif "secant" in msg.lower() or "tangent" in msg.lower() or "slope" in msg.lower():
            reply = (
                "The secant line measures the average rate of change between two distinct points (Δy/Δx), "
                "like calculating your average highway speed. The tangent line measures the instantaneous rate of change "
                "at a single exact point, which is the limit of the secant slopes as Δx approaches zero."
            )
        elif "tree" in msg.lower() or "bst" in msg.lower() or "o(n)" in msg.lower():
            reply = (
                "In a balanced Binary Search Tree, searching takes O(log n) time because each comparison eliminates half the remaining nodes. "
                "However, if keys are inserted in sorted order without balancing (like an AVL or Red-Black tree), "
                "the tree degenerates into a linear linked list with O(n) search time."
            )
        else:
            reply = f"AI Tutor Response to '{msg}': The key takeaway is to verify boundary continuity and foundational definitions before computing intermediate steps."

        return TutorChatResponse(
            session_id=session_id,
            reply=reply,
            language=session.language,
            suggested_actions=["Resume video playback", "Ask for a step-by-step example", "Open lesson plan editor"],
            grounded_sources=sources or ["Core Course Syllabus"]
        )


# Global singleton instance
interaction_service = InteractionService()
