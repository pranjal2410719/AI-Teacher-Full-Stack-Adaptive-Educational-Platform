# Multilingual Support & Localization Architecture

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)](../README.md)
[![Neural Voices](https://img.shields.io/badge/Neural%20TTS-edge--tts%20%7C%20gTTS-blue.svg)](#neural-voice-pipeline--voice-mappings)
[![Languages](https://img.shields.io/badge/Languages-English%20%7C%20Hindi%20(Devanagari)-orange.svg)](#multilingual-architecture--design-principles)
[![Mid-Session Switch](https://img.shields.io/badge/Language%20Switch-State--Preserving-purple.svg)](#mid-session-dynamic-language-switching)

This document details the multilingual engineering and localization architecture of the **AI Teacher** platform, explaining how the system provides native-quality instruction in English and Hindi across neural speech synthesis, avatar lip-sync, visual slide typography, interactive misconception evaluation, and dynamic mid-session language switching.

---

## Table of Contents

- [1. Multilingual Architecture & Design Principles](#1-multilingual-architecture-design-principles)
- [2. Neural Voice Pipeline & Voice Mappings](#2-neural-voice-pipeline-voice-mappings)
  - [Supported Neural Voices](#supported-neural-voices)
  - [Three-Tier Fallback Hierarchy](#three-tier-fallback-hierarchy)
- [3. Devanagari Typography & Unicode Rendering in Video Slides](#3-devanagari-typography-unicode-rendering-in-video-slides)
  - [Font Configuration & Bidi Support](#font-configuration-bidi-support)
  - [Combining Mathematical LaTeX with Hindi Explanatory Text](#combining-mathematical-latex-with-hindi-explanatory-text)
- [4. Mid-Session Dynamic Language Switching](#4-mid-session-dynamic-language-switching)
  - [State Preservation Architecture](#state-preservation-architecture)
  - [Language Switch Execution Flow](#language-switch-execution-flow)
- [5. Phonetic Viseme Synchronization for Hindi & English](#5-phonetic-viseme-synchronization-for-hindi-english)
- [6. Verification & E2E Test Scenarios](#6-verification-e2e-test-scenarios)
- [7. Navigation & Related Documentation](#7-navigation-related-documentation)

---

## 1. Multilingual Architecture & Design Principles

Equal access to high-quality STEM education requires breaking linguistic barriers. Traditional educational content is predominantly produced in English, while learners in regional language environments struggle with technical comprehension.

The AI Teacher platform is engineered from the ground up for native multilingual pedagogy:
1. **No Linguistic Degradation**: Explanations in Hindi utilize natural pedagogical phrasing (e.g., *सीमा (Limit)*, *सांतत्य (Continuity)*, *अवकलन (Differentiation)*) while preserving mathematical rigor.
2. **Synchronized Multilingual Media**: Video slides render native Devanagari typography paired with neural voice synthesis.
3. **Conversational Fluidity**: Students can switch languages at any moment during a lesson without losing their place, concept mastery history, or active misconception diagnoses.

---

## 2. Neural Voice Pipeline & Voice Mappings

Audio synthesis is managed by `tts_service.py`, interfacing with neural text-to-speech providers to generate high-fidelity speech without requiring paid cloud API keys.

### Supported Neural Voices

| Language | Accent / Locale | Gender | Default Voice Name | Provider |
|---|---|---|---|---|
| **English** | United States (`en-US`) | Male (Default) | `en-US-GuyNeural` | Microsoft Edge Neural |
| **English** | United States (`en-US`) | Female | `en-US-AriaNeural` | Microsoft Edge Neural |
| **English** | India (`en-IN`) | Male | `en-IN-PrabhatNeural` | Microsoft Edge Neural |
| **Hindi** | India (`hi-IN`) | Male (Default) | `hi-IN-MadhurNeural` | Microsoft Edge Neural |
| **Hindi** | India (`hi-IN`) | Female | `hi-IN-SwaraNeural` | Microsoft Edge Neural |
| **Spanish** | Spain (`es-ES`) | Male | `es-ES-AlvaroNeural` | Microsoft Edge Neural |
| **French** | France (`fr-FR`) | Male | `fr-FR-HenriNeural` | Microsoft Edge Neural |
| **German** | Germany (`de-DE`) | Male | `de-DE-ConradNeural` | Microsoft Edge Neural |

### Three-Tier Fallback Hierarchy

To ensure uninterrupted video generation regardless of network status or firewall restrictions:

```
[Lesson Script Text]
         │
         ▼
[Tier 1: edge-tts (Microsoft Edge Neural WebSocket)] ──► Success: Studio Audio
         │ (On Network / Connection Timeout)
         ▼
[Tier 2: gTTS (Google Translate HTTP Audio)]        ──► Success: Natural Audio
         │ (On Complete Network Failure)
         ▼
[Tier 3: Local Offline Harmonic PCM Synthesizer]    ──► Success: Resilient Audio
```

1. **Tier 1 (`edge-tts`)**: Delivers ultra-realistic, expressive neural speech with natural prosody and inflection.
2. **Tier 2 (`gTTS`)**: If WebSocket connections to Edge endpoints are restricted, the system seamlessly falls back to Google Translate TTS.
3. **Tier 3 (Local PCM Synthesizer)**: If the host is completely offline, the system generates frequency-modulated harmonic audio waveforms to ensure video rendering completes without errors.

---

## 3. Devanagari Typography & Unicode Rendering in Video Slides

Rendering Hindi text in video slides presents unique technical requirements: complex conjunct consonants, diacritics (matras), and bi-directional alignment when combined with Latin mathematical variables.

### Font Configuration & Bidi Support
Slide renderers (`slide_render_service.py`) automatically detect Unicode scripts and configure appropriate typography:
- **Primary Devanagari Fonts**: DejaVu Sans, FreeSans, Noto Sans Devanagari, or Lohit Devanagari.
- **Font Fallback Resolver**: If a specific glyph is absent, the renderer falls back to Unicode system fonts to prevent replacement squares (tofu characters).

### Combining Mathematical LaTeX with Hindi Explanatory Text

In STEM subjects like calculus, formulas are rendered with standard mathematical notation while titles, descriptions, and bullet points render in Devanagari:

```
+---------------------------------------------------------------------------------------+
|  गणित: सीमा और सांतत्य (Mathematics: Limits & Continuity)                              |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|  • बायीं और दायीं सीमा की परिभाषा (Definition of Left and Right Limits):             |
|                                                                                       |
|                          \lim_{x \to c^-} f(x) = L_1                                  |
|                          \lim_{x \to c^+} f(x) = L_2                                  |
|                                                                                       |
|  • यदि L_1 = L_2 = L, तो बिंदु c पर सीमा मौजूद है।                                     |
|    (If L1 = L2 = L, then the limit exists at point c.)                                |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

---

## 4. Mid-Session Dynamic Language Switching

Learners can switch instruction language at any time during playback using the `/api/v1/interactive/switch-language` endpoint or side-panel tutor chat.

### State Preservation Architecture

```
[Session State: sess_101]
  ├── active_concept_id: "One-Sided Limits"
  ├── mastered_concepts: ["Limits Definition"]
  ├── diagnosed_misconceptions: ["Confusing continuity with limit existence"]
  └── language: "en" ──► [Switch Request: "hi"] ──► language: "hi" (Context Preserved)
```

When switching language:
1. **No Reset**: The student does NOT restart the lesson or lose progress.
2. **Context Migration**: The active concept, session history, and misconception logs remain intact.
3. **Localized Summary**: The AI Teacher generates an instant translated recap in the new language to anchor the transition.
4. **Subsequent Interaction**: All subsequent checkpoint questions, tutor chat responses, and final quiz questions are delivered in the new target language.

### Language Switch Execution Flow

#### Example Request (`POST /api/v1/interactive/switch-language`)
```json
{
  "session_id": "sess_101",
  "target_language": "hi",
  "current_concept_id": "One-Sided Limits"
}
```

#### Example Response (`200 OK`)
```json
{
  "language": "hi",
  "translated_summary": "अब हम सीमा (Limits) की अवधारणा को हिंदी में समझेंगे। यदि बायीं सीमा (Left-Hand Limit) और दायीं सीमा (Right-Hand Limit) समान हैं, तो सीमा मौजूद होती है।",
  "next_prompt": "क्या आप सीमा और सांतत्य (Continuity) के अंतर पर एक उदाहरण देखना चाहते हैं?"
}
```

---

## 5. Phonetic Viseme Synchronization for Hindi & English

The 2.5D talking avatar generator (`avatar_service.py`) synchronizes lip movements directly from audio RMS energy envelopes rather than relying exclusively on English-only phonetic dictionaries.

1. **Language-Agnostic Energy Sampling**: The audio stream is sampled at 100ms intervals, capturing acoustic intensity and phonetic plosives regardless of whether the speaker is vocalizing English vowels or Hindi phonemes (e.g., स्वर like *आ, ई, ऊ* or व्यंजन like *क, प, म*).
2. **Natural Viseme Modulation**:
   - Soft Hindi vowels trigger `viseme_slight` or `viseme_open`.
   - Strong aspirates (महाप्राण ध्वनियां like *ख, घ, थ, भ*) dynamically trigger `viseme_wide` and `viseme_o`.
3. **Realistic Rapport**: The avatar maintains continuous blinking and breathing bobbing throughout multilingual narration.

---

## 6. Verification & E2E Test Scenarios

Multilingual capabilities are continuously verified via the automated E2E test suite:

### Test Coverage Highlights:
- **Tier 2 (Boundary & Corner Cases)**:
  - `test_devanagari_and_unicode_resilience`: Verifies parsing, chunking, and rendering of complex Devanagari Hindi text and LaTeX mathematical symbols without encoding corruption.
- **Tier 3 (Cross-Feature Combinations)**:
  - `test_multilingual_switch_flow`: Verifies context preservation and localized response delivery during a mid-lesson language transition.
- **Tier 4 (Real-World Persona Scenarios)**:
  - `Scenario 1 (High School Calculus in Hindi)`: Full end-to-end execution of a Hindi calculus lesson covering Devanagari slide generation, `hi-IN-MadhurNeural` audio narration, Hindi checkpoint pause evaluation, and Hindi quiz grading.

---

## 7. Navigation & Related Documentation

| Document | Description |
|---|---|
| [Project Overview (README.md)](../README.md) | High-level project summary, features, and quickstart |
| [System Architecture](architecture.md) | 5-tier architecture, pedagogical state machines, and ADRs |
| [API Specification](api_specification.md) | Comprehensive reference for all 25 REST endpoints |
| [Setup & Deployment Guide](setup_and_deployment.md) | Docker Compose, `./run.sh`, and local setup instructions |
| [User Guide & Demo Video Walkthrough](user_guide.md) | End-to-end user journey and demo video generation |
| [E2E Testing Readiness Declaration](../TEST_READY.md) | 56/56 test suite readiness verification report |
