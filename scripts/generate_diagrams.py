import os
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_svg(output_svg_path):
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 980" width="1440" height="980" style="background:#0B0F19; font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif;">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F172A" />
      <stop offset="50%" stop-color="#0B0F19" />
      <stop offset="100%" stop-color="#080C14" />
    </linearGradient>
    <linearGradient id="primaryGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6" />
      <stop offset="100%" stop-color="#8B5CF6" />
    </linearGradient>
    <linearGradient id="emeraldGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#059669" />
      <stop offset="100%" stop-color="#10B981" />
    </linearGradient>
    <linearGradient id="amberGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#D97706" />
      <stop offset="100%" stop-color="#F59E0B" />
    </linearGradient>
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7C3AED" />
      <stop offset="100%" stop-color="#A855F7" />
    </linearGradient>
    <linearGradient id="roseGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#E11D48" />
      <stop offset="100%" stop-color="#F43F5E" />
    </linearGradient>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0891B2" />
      <stop offset="100%" stop-color="#06B6D4" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1440" height="980" fill="url(#bgGrad)"/>
  
  <!-- Subtle Grid Overlay -->
  <g opacity="0.04" stroke="#FFFFFF" stroke-width="1">
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none"/>
    </pattern>
    <rect width="1440" height="980" fill="url(#grid)"/>
  </g>

  <!-- Header Section -->
  <g transform="translate(40, 25)">
    <!-- Header Badge -->
    <rect x="0" y="0" width="1360" height="75" rx="12" fill="#1E293B" stroke="#334155" stroke-width="1.5" filter="url(#cardShadow)"/>
    <rect x="0" y="0" width="6" height="75" rx="3" fill="url(#primaryGrad)"/>
    
    <text x="25" y="32" fill="#F8FAFC" font-size="20" font-weight="700" letter-spacing="0.5">AI TEACHER — Full-Stack Adaptive Educational Platform</text>
    <text x="25" y="55" fill="#94A3B8" font-size="13">High-Level System Architecture: 8-Phase Human Teaching Loop • Hybrid Neural Video • RAG Knowledge Retrieval</text>
    
    <!-- Status Badges -->
    <g transform="translate(940, 20)">
      <rect x="0" y="0" width="125" height="34" rx="17" fill="#064E3B" stroke="#059669" stroke-width="1"/>
      <circle cx="16" cy="17" r="5" fill="#10B981"/>
      <text x="30" y="22" fill="#ECFDF5" font-size="12" font-weight="600">56/56 Tests Pass</text>
      
      <rect x="135" y="0" width="135" height="34" rx="17" fill="#1E1B4B" stroke="#4338CA" stroke-width="1"/>
      <circle cx="151" cy="17" r="5" fill="#818CF8"/>
      <text x="165" y="22" fill="#EEF2FF" font-size="12" font-weight="600">FastAPI + React</text>
      
      <rect x="280" y="0" width="130" height="34" rx="17" fill="#312E81" stroke="#6366F1" stroke-width="1"/>
      <circle cx="296" cy="17" r="5" fill="#A5B4FC"/>
      <text x="310" y="22" fill="#EEF2FF" font-size="12" font-weight="600">FFmpeg 720p</text>
    </g>
  </g>

  <!-- TIER 1: Presentation Layer (Frontend) -->
  <g transform="translate(40, 120)">
    <rect width="1360" height="135" rx="12" fill="#111827" stroke="#1F2937" stroke-width="1.5" filter="url(#cardShadow)"/>
    <rect x="15" y="15" width="220" height="26" rx="6" fill="#1E3A8A"/>
    <text x="25" y="33" fill="#93C5FD" font-size="12" font-weight="700" letter-spacing="0.5">TIER 1: PRESENTATION (REACT / VITE)</text>
    
    <!-- UI Component Cards -->
    <g transform="translate(20, 50)">
      <!-- Card 1: Ingestion UI -->
      <rect x="0" y="0" width="175" height="70" rx="8" fill="#1F2937" stroke="#374151" stroke-width="1"/>
      <text x="12" y="24" fill="#38BDF8" font-size="12" font-weight="600">Document Dropzone</text>
      <text x="12" y="42" fill="#9CA3AF" font-size="10">PDF, DOCX, PPTX, TXT</text>
      <text x="12" y="56" fill="#6B7280" font-size="9">Parametric Topic Ingest</text>

      <!-- Card 2: Profile Config -->
      <rect x="190" y="0" width="175" height="70" rx="8" fill="#1F2937" stroke="#374151" stroke-width="1"/>
      <text x="202" y="24" fill="#38BDF8" font-size="12" font-weight="600">Learner Profile Setup</text>
      <text x="202" y="42" fill="#9CA3AF" font-size="10">Beg / Inter / Adv Level</text>
      <text x="202" y="56" fill="#6B7280" font-size="9">5-60m Budget • EN/HI</text>

      <!-- Card 3: Plan Reviewer -->
      <rect x="380" y="0" width="175" height="70" rx="8" fill="#1F2937" stroke="#374151" stroke-width="1"/>
      <text x="392" y="24" fill="#38BDF8" font-size="12" font-weight="600">Lesson Plan Reviewer</text>
      <text x="392" y="42" fill="#9CA3AF" font-size="10">Interactive Reordering</text>
      <text x="392" y="56" fill="#6B7280" font-size="9">Visual Slide Spec Preview</text>

      <!-- Card 4: Hybrid Video Player -->
      <rect x="570" y="0" width="200" height="70" rx="8" fill="#1E1B4B" stroke="#4338CA" stroke-width="1.2"/>
      <text x="582" y="24" fill="#A5B4FC" font-size="12" font-weight="700">Interactive Video Player</text>
      <text x="582" y="42" fill="#C7D2FE" font-size="10">HTML5 Range Stream (206)</text>
      <text x="582" y="56" fill="#818CF8" font-size="9">Pause Checkpoint Overlays</text>

      <!-- Card 5: Misconception Drawer -->
      <rect x="785" y="0" width="175" height="70" rx="8" fill="#1F2937" stroke="#374151" stroke-width="1"/>
      <text x="797" y="24" fill="#FBBF24" font-size="12" font-weight="600">Misconception Drawer</text>
      <text x="797" y="42" fill="#9CA3AF" font-size="10">Scaffolded Analogies</text>
      <text x="797" y="56" fill="#6B7280" font-size="9">Follow-Up Verifications</text>

      <!-- Card 6: AI Tutor Chat -->
      <rect x="975" y="0" width="165" height="70" rx="8" fill="#1F2937" stroke="#374151" stroke-width="1"/>
      <text x="987" y="24" fill="#34D399" font-size="12" font-weight="600">Grounded Tutor Chat</text>
      <text x="987" y="42" fill="#9CA3AF" font-size="10">Side-Panel RAG Q&amp;A</text>
      <text x="987" y="56" fill="#6B7280" font-size="9">Mid-Session Lang Switch</text>

      <!-- Card 7: Quiz & Reports -->
      <rect x="1155" y="0" width="165" height="70" rx="8" fill="#1F2937" stroke="#374151" stroke-width="1"/>
      <text x="1167" y="24" fill="#F43F5E" font-size="12" font-weight="600">Quiz &amp; Analytics</text>
      <text x="1167" y="42" fill="#9CA3AF" font-size="10">Diagnostic Reports</text>
      <text x="1167" y="56" fill="#6B7280" font-size="9">Persistent Mastery Graph</text>
    </g>
  </g>

  <!-- Arrow T1 -> T2 -->
  <g stroke="#3B82F6" stroke-width="2" opacity="0.7" fill="none">
    <path d="M 720 255 L 720 275" marker-end="url(#arrow)"/>
  </g>

  <!-- TIER 2: API Gateway Layer (FastAPI :8000) -->
  <g transform="translate(40, 275)">
    <rect width="1360" height="90" rx="12" fill="#111827" stroke="#1F2937" stroke-width="1.5" filter="url(#cardShadow)"/>
    <rect x="15" y="12" width="220" height="24" rx="6" fill="#1E293B"/>
    <text x="25" y="28" fill="#CBD5E1" font-size="12" font-weight="700" letter-spacing="0.5">TIER 2: REST API GATEWAY (FASTAPI :8000)</text>

    <g transform="translate(20, 42)">
      <!-- Route Box 1 -->
      <rect x="0" y="0" width="210" height="36" rx="6" fill="#0F172A" stroke="#059669" stroke-width="1"/>
      <text x="10" y="16" fill="#10B981" font-size="10" font-weight="700">/api/v1/materials/*</text>
      <text x="10" y="29" fill="#94A3B8" font-size="9">upload, topic, query, metadata</text>

      <!-- Route Box 2 -->
      <rect x="225" y="0" width="210" height="36" rx="6" fill="#0F172A" stroke="#2563EB" stroke-width="1"/>
      <text x="235" y="16" fill="#60A5FA" font-size="10" font-weight="700">/api/v1/lessons/*</text>
      <text x="235" y="29" fill="#94A3B8" font-size="9">plan, update, list, editor</text>

      <!-- Route Box 3 -->
      <rect x="450" y="0" width="225" height="36" rx="6" fill="#0F172A" stroke="#7C3AED" stroke-width="1"/>
      <text x="460" y="16" fill="#C084FC" font-size="10" font-weight="700">/api/v1/video/*</text>
      <text x="460" y="29" fill="#94A3B8" font-size="9">generate, status, stream, manifest</text>

      <!-- Route Box 4 -->
      <rect x="690" y="0" width="215" height="36" rx="6" fill="#0F172A" stroke="#D97706" stroke-width="1"/>
      <text x="700" y="16" fill="#FBBF24" font-size="10" font-weight="700">/api/v1/interactive/*</text>
      <text x="700" y="29" fill="#94A3B8" font-size="9">evaluate, chat, switch-lang</text>

      <!-- Route Box 5 -->
      <rect x="920" y="0" width="210" height="36" rx="6" fill="#0F172A" stroke="#E11D48" stroke-width="1"/>
      <text x="930" y="16" fill="#FB7185" font-size="10" font-weight="700">/api/v1/assessment/*</text>
      <text x="930" y="29" fill="#94A3B8" font-size="9">generate, submit, report</text>

      <!-- Route Box 6 -->
      <rect x="1145" y="0" width="175" height="36" rx="6" fill="#0F172A" stroke="#0891B2" stroke-width="1"/>
      <text x="1155" y="16" fill="#22D3EE" font-size="10" font-weight="700">/api/v1/profile &amp; health</text>
      <text x="1155" y="29" fill="#94A3B8" font-size="9">history, recommend, /health</text>
    </g>
  </g>

  <!-- Arrow T2 -> T3 -->
  <g stroke="#8B5CF6" stroke-width="2" opacity="0.7" fill="none">
    <path d="M 720 365 L 720 385"/>
  </g>

  <!-- TIER 3: Core Pedagogical Services (R1-R5) -->
  <g transform="translate(40, 385)">
    <rect width="1360" height="175" rx="12" fill="#111827" stroke="#1F2937" stroke-width="1.5" filter="url(#cardShadow)"/>
    <rect x="15" y="15" width="260" height="26" rx="6" fill="#4C1D95"/>
    <text x="25" y="33" fill="#DDD6FE" font-size="12" font-weight="700" letter-spacing="0.5">TIER 3: CORE PEDAGOGICAL SERVICES (R1 - R5)</text>

    <g transform="translate(20, 52)">
      <!-- Service 1: R1 Ingestion & RAG -->
      <rect x="0" y="0" width="250" height="105" rx="8" fill="#064E3B" fill-opacity="0.3" stroke="#059669" stroke-width="1.2"/>
      <text x="14" y="24" fill="#34D399" font-size="13" font-weight="700">R1: Ingestion &amp; RAG Engine</text>
      <text x="14" y="44" fill="#E2E8F0" font-size="11">• Multi-Format Parsers (PDF/DOCX/PPT)</text>
      <text x="14" y="62" fill="#E2E8F0" font-size="11">• Structure-Aware Chunking &amp; Overlap</text>
      <text x="14" y="80" fill="#E2E8F0" font-size="11">• Dense Cosine + Okapi BM25 RAG</text>
      <text x="14" y="96" fill="#94A3B8" font-size="10">Parametric Topic Knowledge Generator</text>

      <!-- Service 2: R2 Lesson Planner -->
      <rect x="265" y="0" width="255" height="105" rx="8" fill="#1E3A8A" fill-opacity="0.3" stroke="#2563EB" stroke-width="1.2"/>
      <text x="279" y="24" fill="#60A5FA" font-size="13" font-weight="700">R2: Adaptive Lesson Planner</text>
      <text x="279" y="44" fill="#E2E8F0" font-size="11">• Pedagogical 8-Phase Flow Sequencing</text>
      <text x="279" y="62" fill="#E2E8F0" font-size="11">• Duration Scaling (5m concise - 60m deep)</text>
      <text x="279" y="80" fill="#E2E8F0" font-size="11">• Multi-Level Cognitive Adaptation</text>
      <text x="279" y="96" fill="#94A3B8" font-size="10">Visual Slide Spec Synthesis &amp; Checkpoints</text>

      <!-- Service 3: R3 Video Stitcher -->
      <rect x="535" y="0" width="270" height="105" rx="8" fill="#581C87" fill-opacity="0.3" stroke="#7C3AED" stroke-width="1.2"/>
      <text x="549" y="24" fill="#C084FC" font-size="13" font-weight="700">R3: Hybrid Video Stitcher</text>
      <text x="549" y="44" fill="#E2E8F0" font-size="11">• Multi-Stage Background Worker</text>
      <text x="549" y="62" fill="#E2E8F0" font-size="11">• FFmpeg H.264/AAC Concat Demuxer</text>
      <text x="549" y="80" fill="#E2E8F0" font-size="11">• Chapter Timing &amp; Pause Markers</text>
      <text x="549" y="96" fill="#94A3B8" font-size="10">VideoManifest JSON Generator</text>

      <!-- Service 4: R4 Interactive Loop -->
      <rect x="820" y="0" width="260" height="105" rx="8" fill="#78350F" fill-opacity="0.3" stroke="#D97706" stroke-width="1.2"/>
      <text x="834" y="24" fill="#FBBF24" font-size="13" font-weight="700">R4: Interactive Teaching Loop</text>
      <text x="834" y="44" fill="#E2E8F0" font-size="11">• LLM Rubric Student Evaluation</text>
      <text x="834" y="62" fill="#E2E8F0" font-size="11">• Misconception Diagnosis &amp; Scaffolding</text>
      <text x="834" y="80" fill="#E2E8F0" font-size="11">• Analogy Generation &amp; Follow-Up Checks</text>
      <text x="834" y="96" fill="#94A3B8" font-size="10">Mid-Session Multilingual Switching State</text>

      <!-- Service 5: R5 Assessment & Profile -->
      <rect x="1095" y="0" width="225" height="105" rx="8" fill="#881337" fill-opacity="0.3" stroke="#E11D48" stroke-width="1.2"/>
      <text x="1109" y="24" fill="#FB7185" font-size="13" font-weight="700">R5: Assessment &amp; Profile</text>
      <text x="1109" y="44" fill="#E2E8F0" font-size="11">• Dynamic Post-Lesson Quiz Gen</text>
      <text x="1109" y="62" fill="#E2E8F0" font-size="11">• Diagnostic Learning Reports</text>
      <text x="1109" y="80" fill="#E2E8F0" font-size="11">• Cross-Session Profile Store</text>
      <text x="1109" y="96" fill="#94A3B8" font-size="10">Adaptive Next-Step Recommender</text>
    </g>
  </g>

  <!-- Arrow T3 -> T4 -->
  <g stroke="#10B981" stroke-width="2" opacity="0.7" fill="none">
    <path d="M 720 560 L 720 580"/>
  </g>

  <!-- TIER 4: Media & Subject-Aware Compute Engines -->
  <g transform="translate(40, 580)">
    <rect width="1360" height="175" rx="12" fill="#111827" stroke="#1F2937" stroke-width="1.5" filter="url(#cardShadow)"/>
    <rect x="15" y="15" width="300" height="26" rx="6" fill="#047857"/>
    <text x="25" y="33" fill="#D1FAE5" font-size="12" font-weight="700" letter-spacing="0.5">TIER 4: MEDIA &amp; VISUAL COMPUTE PIPELINE</text>

    <g transform="translate(20, 52)">
      <!-- Engine 1: Neural TTS -->
      <rect x="0" y="0" width="305" height="105" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
      <text x="14" y="24" fill="#38BDF8" font-size="13" font-weight="700">Multilingual Neural TTS Engine</text>
      <text x="14" y="44" fill="#CBD5E1" font-size="11">• edge-tts (en-US-GuyNeural, hi-IN-Madhur)</text>
      <text x="14" y="62" fill="#CBD5E1" font-size="11">• Instant gTTS HTTP Secondary Fallback</text>
      <text x="14" y="80" fill="#CBD5E1" font-size="11">• Local Harmonic PCM Synthesizer</text>
      <text x="14" y="96" fill="#64748B" font-size="10">Exact Audio Duration &amp; Sample Alignment</text>

      <!-- Engine 2: 2.5D Viseme Avatar -->
      <rect x="320" y="0" width="315" height="105" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
      <text x="334" y="24" fill="#A78BFA" font-size="13" font-weight="700">2.5D Audio-Driven Viseme Avatar</text>
      <text x="334" y="44" fill="#CBD5E1" font-size="11">• RMS Energy Envelope &amp; 5 Viseme States</text>
      <text x="334" y="62" fill="#CBD5E1" font-size="11">• 3.2s Periodic Blinking &amp; Natural Bobbing</text>
      <text x="334" y="80" fill="#CBD5E1" font-size="11">• Real-Time Studio HUD &amp; Equalizer Wave</text>
      <text x="334" y="96" fill="#64748B" font-size="10">Wav2Lip Open-Source CLI Backend Hook</text>

      <!-- Engine 3: Subject-Aware Slide Renderers -->
      <rect x="650" y="0" width="375" height="105" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
      <text x="664" y="24" fill="#FCD34D" font-size="13" font-weight="700">Subject-Aware Visual Slide Renderers</text>
      <text x="664" y="44" fill="#CBD5E1" font-size="11">• Math: LaTeX Formulations &amp; Function Graphs</text>
      <text x="664" y="62" fill="#CBD5E1" font-size="11">• CS: Pygments Syntax-Highlighted IDE Window</text>
      <text x="664" y="80" fill="#CBD5E1" font-size="11">• Biology: Cellular Structure Callout Diagrams</text>
      <text x="664" y="96" fill="#64748B" font-size="10">History: Horizontal Chronological Timeline</text>

      <!-- Engine 4: FFmpeg Stitcher -->
      <rect x="1040" y="0" width="280" height="105" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
      <text x="1054" y="24" fill="#F43F5E" font-size="13" font-weight="700">FFmpeg Assembly &amp; Stitcher</text>
      <text x="1054" y="44" fill="#CBD5E1" font-size="11">• 1280x720 30fps H.264 / AAC Encoding</text>
      <text x="1054" y="62" fill="#CBD5E1" font-size="11">• Concat Demuxer with Zero Transcode Loss</text>
      <text x="1054" y="80" fill="#CBD5E1" font-size="11">• -movflags +faststart Web Streaming</text>
      <text x="1054" y="96" fill="#64748B" font-size="10">Real-Time Stage-by-Stage Progress Events</text>
    </g>
  </g>

  <!-- Arrow T4 -> T5 -->
  <g stroke="#EC4899" stroke-width="2" opacity="0.7" fill="none">
    <path d="M 720 755 L 720 775"/>
  </g>

  <!-- TIER 5: AI Providers, Vector Store & Storage -->
  <g transform="translate(40, 775)">
    <rect width="1360" height="155" rx="12" fill="#111827" stroke="#1F2937" stroke-width="1.5" filter="url(#cardShadow)"/>
    <rect x="15" y="15" width="280" height="26" rx="6" fill="#831843"/>
    <text x="25" y="33" fill="#FCE7F3" font-size="12" font-weight="700" letter-spacing="0.5">TIER 5: AI PROVIDERS, DATA &amp; STORAGE</text>

    <g transform="translate(20, 52)">
      <!-- AI Providers -->
      <rect x="0" y="0" width="315" height="85" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <text x="14" y="24" fill="#F472B6" font-size="12" font-weight="700">Free-Tier LLM Cloud Providers</text>
      <text x="14" y="44" fill="#CBD5E1" font-size="11">• Groq Cloud (Llama-3-70B &amp; 8B-Versatile)</text>
      <text x="14" y="62" fill="#CBD5E1" font-size="11">• Google AI Studio (Gemini 1.5 Flash Free)</text>
      <text x="14" y="78" fill="#64748B" font-size="10">Offline Parametric Heuristic Fallback Engine</text>

      <!-- Vector Store -->
      <rect x="330" y="0" width="325" height="85" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <text x="344" y="24" fill="#38BDF8" font-size="12" font-weight="700">Vector Storage &amp; Lexical Search</text>
      <text x="344" y="44" fill="#CBD5E1" font-size="11">• Pure-Python Numpy Cosine Vector Store</text>
      <text x="344" y="62" fill="#CBD5E1" font-size="11">• Okapi BM25 Lexical Inverted Index</text>
      <text x="344" y="78" fill="#64748B" font-size="10">Optional Milvus 2.4.0 Container on Port 19530</text>

      <!-- Database & Profiles -->
      <rect x="670" y="0" width="330" height="85" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <text x="684" y="24" fill="#FBBF24" font-size="12" font-weight="700">Profile &amp; Session Persistence</text>
      <text x="684" y="44" fill="#CBD5E1" font-size="11">• SQLite Database / Structured JSON Records</text>
      <text x="684" y="62" fill="#CBD5E1" font-size="11">• Cross-Session Concept Mastery Scores</text>
      <text x="684" y="78" fill="#64748B" font-size="10">Adaptive Recommendation Knowledge Graph</text>

      <!-- Local File Assets -->
      <rect x="1015" y="0" width="305" height="85" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <text x="1029" y="24" fill="#34D399" font-size="12" font-weight="700">File Storage Hierarchy</text>
      <text x="1029" y="44" fill="#CBD5E1" font-size="11">• data/uploads/ &amp; data/plans/</text>
      <text x="1029" y="62" fill="#CBD5E1" font-size="11">• data/rendered_videos/ &amp; manifests/</text>
      <text x="1029" y="78" fill="#64748B" font-size="10">data/quizzes/, reports/ &amp; profiles/</text>
    </g>
  </g>

  <!-- Footer Info -->
  <g transform="translate(40, 945)">
    <text x="0" y="15" fill="#64748B" font-size="11">AI Teacher Platform • Comprehensive 5-Tier Architecture • Zero-Cost Free-Tier APIs &amp; Open-Source Local Pipelines</text>
    <text x="1360" y="15" text-anchor="end" fill="#64748B" font-size="11">AI Innovation Hackathon 2026</text>
  </g>
</svg>"""
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated SVG at: {output_svg_path}")

def generate_png(output_png_path):
    W, H = 1440, 980
    img = Image.new("RGB", (W, H), color=(11, 15, 25))
    draw = ImageDraw.Draw(img)

    # Load system fonts
    font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_reg_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    title_font = ImageFont.truetype(font_bold_path, 20)
    sub_font = ImageFont.truetype(font_reg_path, 12)
    section_font = ImageFont.truetype(font_bold_path, 12)
    card_title_font = ImageFont.truetype(font_bold_path, 11)
    card_body_font = ImageFont.truetype(font_reg_path, 10)
    card_foot_font = ImageFont.truetype(font_reg_path, 9)
    badge_font = ImageFont.truetype(font_bold_path, 11)

    # 1. Header Box
    draw.rounded_rectangle([(40, 25), (1400, 100)], radius=10, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.rounded_rectangle([(40, 25), (46, 100)], radius=3, fill=(59, 130, 246))
    draw.text((65, 38), "AI TEACHER — Full-Stack Adaptive Educational Platform", font=title_font, fill=(248, 250, 252))
    draw.text((65, 68), "High-Level System Architecture: 8-Phase Human Teaching Loop • Hybrid Neural Video • RAG Knowledge Retrieval", font=sub_font, fill=(148, 163, 184))

    # Badges
    draw.rounded_rectangle([(970, 42), (1095, 78)], radius=18, fill=(6, 78, 59), outline=(5, 150, 105), width=1)
    draw.ellipse([(982, 55), (992, 65)], fill=(16, 185, 129))
    draw.text((1002, 53), "56/56 Tests Pass", font=badge_font, fill=(236, 253, 245))

    draw.rounded_rectangle([(1110, 42), (1245, 78)], radius=18, fill=(30, 27, 75), outline=(67, 56, 202), width=1)
    draw.ellipse([(1122, 55), (1132, 65)], fill=(129, 140, 248))
    draw.text((1140, 53), "FastAPI + React", font=badge_font, fill=(238, 242, 255))

    draw.rounded_rectangle([(1260, 42), (1385, 78)], radius=18, fill=(49, 46, 129), outline=(99, 102, 241), width=1)
    draw.ellipse([(1272, 55), (1282, 65)], fill=(165, 180, 252))
    draw.text((1290, 53), "FFmpeg 720p", font=badge_font, fill=(238, 242, 255))

    # 2. Tier 1: Presentation Layer
    draw.rounded_rectangle([(40, 120), (1400, 255)], radius=10, fill=(17, 24, 39), outline=(31, 41, 55), width=2)
    draw.rounded_rectangle([(55, 130), (330, 156)], radius=6, fill=(30, 58, 138))
    draw.text((65, 137), "TIER 1: PRESENTATION (REACT / VITE)", font=section_font, fill=(147, 197, 253))

    ui_cards = [
        (60, 170, 175, "Document Dropzone", "PDF, DOCX, PPTX, TXT", "Parametric Topic Ingest", (56, 189, 248)),
        (250, 170, 175, "Learner Profile Setup", "Beg / Inter / Adv Level", "5-60m Budget • EN/HI", (56, 189, 248)),
        (440, 170, 175, "Lesson Plan Reviewer", "Interactive Reordering", "Visual Slide Spec Preview", (56, 189, 248)),
        (630, 170, 200, "Interactive Video Player", "HTML5 Range Stream (206)", "Pause Checkpoint Overlays", (165, 180, 252)),
        (845, 170, 175, "Misconception Drawer", "Scaffolded Analogies", "Follow-Up Verifications", (251, 191, 36)),
        (1035, 170, 170, "Grounded Tutor Chat", "Side-Panel RAG Q&A", "Mid-Session Lang Switch", (52, 211, 153)),
        (1220, 170, 165, "Quiz & Analytics", "Diagnostic Reports", "Persistent Mastery Graph", (244, 63, 94))
    ]
    for (x, y, w, t, b1, b2, col) in ui_cards:
        draw.rounded_rectangle([(x, y), (x+w, y+70)], radius=6, fill=(31, 41, 55), outline=(55, 65, 81), width=1)
        draw.text((x+10, y+10), t, font=card_title_font, fill=col)
        draw.text((x+10, y+28), b1, font=card_body_font, fill=(156, 163, 175))
        draw.text((x+10, y+45), b2, font=card_foot_font, fill=(107, 114, 128))

    # Connector T1 -> T2
    draw.line([(720, 255), (720, 275)], fill=(59, 130, 246), width=2)

    # 3. Tier 2: API Gateway Layer
    draw.rounded_rectangle([(40, 275), (1400, 365)], radius=10, fill=(17, 24, 39), outline=(31, 41, 55), width=2)
    draw.rounded_rectangle([(55, 285), (360, 310)], radius=6, fill=(30, 41, 59))
    draw.text((65, 292), "TIER 2: REST API GATEWAY (FASTAPI :8000)", font=section_font, fill=(203, 213, 225))

    api_boxes = [
        (60, 317, 210, "/api/v1/materials/*", "upload, topic, query, metadata", (16, 185, 129)),
        (285, 317, 210, "/api/v1/lessons/*", "plan, update, list, editor", (96, 165, 250)),
        (510, 317, 225, "/api/v1/video/*", "generate, status, stream, manifest", (192, 132, 252)),
        (750, 317, 215, "/api/v1/interactive/*", "evaluate, chat, switch-lang", (251, 191, 36)),
        (980, 317, 210, "/api/v1/assessment/*", "generate, submit, report", (251, 113, 133)),
        (1205, 317, 180, "/api/v1/profile & health", "history, recommend, /health", (34, 211, 238))
    ]
    for (x, y, w, r, d, col) in api_boxes:
        draw.rounded_rectangle([(x, y), (x+w, y+36)], radius=6, fill=(15, 23, 42), outline=col, width=1)
        draw.text((x+10, y+6), r, font=card_title_font, fill=col)
        draw.text((x+10, y+20), d, font=card_foot_font, fill=(148, 163, 184))

    # Connector T2 -> T3
    draw.line([(720, 365), (720, 385)], fill=(139, 92, 246), width=2)

    # 4. Tier 3: Core Pedagogical Services
    draw.rounded_rectangle([(40, 385), (1400, 560)], radius=10, fill=(17, 24, 39), outline=(31, 41, 55), width=2)
    draw.rounded_rectangle([(55, 395), (370, 421)], radius=6, fill=(76, 29, 149))
    draw.text((65, 403), "TIER 3: CORE PEDAGOGICAL SERVICES (R1 - R5)", font=section_font, fill=(221, 214, 254))

    services = [
        (60, 432, 250, "R1: Ingestion & RAG Engine", ["• Multi-Format Parsers (PDF/DOCX/PPT)", "• Structure-Aware Chunking & Overlap", "• Dense Cosine + Okapi BM25 RAG", "Parametric Topic Knowledge Generator"], (52, 211, 153), (5, 150, 105)),
        (325, 432, 255, "R2: Adaptive Lesson Planner", ["• Pedagogical 8-Phase Flow Sequencing", "• Duration Scaling (5m-60m)", "• Multi-Level Cognitive Adaptation", "Visual Slide Spec Synthesis & Checkpoints"], (96, 165, 250), (37, 99, 235)),
        (595, 432, 270, "R3: Hybrid Video Stitcher", ["• Multi-Stage Background Worker", "• FFmpeg H.264/AAC Concat Demuxer", "• Chapter Timing & Pause Markers", "VideoManifest JSON Generator"], (192, 132, 252), (124, 58, 237)),
        (880, 432, 260, "R4: Interactive Teaching Loop", ["• LLM Rubric Student Evaluation", "• Misconception Diagnosis & Scaffolding", "• Analogy Generation & Follow-Up Checks", "Mid-Session Multilingual Switching State"], (251, 191, 36), (217, 119, 6)),
        (1155, 432, 230, "R5: Assessment & Profile", ["• Dynamic Post-Lesson Quiz Gen", "• Diagnostic Learning Reports", "• Cross-Session Profile Store", "Adaptive Next-Step Recommender"], (251, 113, 133), (225, 29, 72))
    ]
    for (x, y, w, title, bullets, col, out_col) in services:
        draw.rounded_rectangle([(x, y), (x+w, y+112)], radius=8, fill=(20, 28, 44), outline=out_col, width=1)
        draw.text((x+12, y+10), title, font=card_title_font, fill=col)
        for i, b in enumerate(bullets):
            f_col = (226, 232, 240) if i < 3 else (148, 163, 184)
            f_font = card_body_font if i < 3 else card_foot_font
            draw.text((x+12, y+30 + i*18), b, font=f_font, fill=f_col)

    # Connector T3 -> T4
    draw.line([(720, 560), (720, 580)], fill=(16, 185, 129), width=2)

    # 5. Tier 4: Media & Visual Compute Pipeline
    draw.rounded_rectangle([(40, 580), (1400, 755)], radius=10, fill=(17, 24, 39), outline=(31, 41, 55), width=2)
    draw.rounded_rectangle([(55, 590), (370, 616)], radius=6, fill=(4, 120, 87))
    draw.text((65, 598), "TIER 4: MEDIA & VISUAL COMPUTE PIPELINE", font=section_font, fill=(209, 250, 229))

    engines = [
        (60, 627, 305, "Multilingual Neural TTS Engine", ["• edge-tts (en-US-GuyNeural, hi-IN-Madhur)", "• Instant gTTS HTTP Secondary Fallback", "• Local Harmonic PCM Synthesizer", "Exact Audio Duration & Sample Alignment"], (56, 189, 248)),
        (380, 627, 315, "2.5D Audio-Driven Viseme Avatar", ["• RMS Energy Envelope & 5 Viseme States", "• 3.2s Periodic Blinking & Natural Bobbing", "• Real-Time Studio HUD & Equalizer Wave", "Wav2Lip Open-Source CLI Backend Hook"], (167, 139, 250)),
        (710, 627, 375, "Subject-Aware Visual Slide Renderers", ["• Math: LaTeX Formulations & Function Graphs", "• CS: Pygments Syntax-Highlighted IDE Window", "• Biology: Cellular Structure Callout Diagrams", "History: Horizontal Chronological Timeline"], (252, 211, 77)),
        (1100, 627, 285, "FFmpeg Assembly & Stitcher", ["• 1280x720 30fps H.264 / AAC Encoding", "• Concat Demuxer with Zero Transcode Loss", "• -movflags +faststart Web Streaming", "Real-Time Stage-by-Stage Progress Events"], (244, 63, 94))
    ]
    for (x, y, w, title, bullets, col) in engines:
        draw.rounded_rectangle([(x, y), (x+w, y+112)], radius=8, fill=(30, 41, 59), outline=(51, 65, 85), width=1)
        draw.text((x+12, y+10), title, font=card_title_font, fill=col)
        for i, b in enumerate(bullets):
            f_col = (203, 213, 225) if i < 3 else (100, 116, 139)
            f_font = card_body_font if i < 3 else card_foot_font
            draw.text((x+12, y+30 + i*18), b, font=f_font, fill=f_col)

    # Connector T4 -> T5
    draw.line([(720, 755), (720, 775)], fill=(236, 72, 153), width=2)

    # 6. Tier 5: AI Providers, Vector Store & Storage
    draw.rounded_rectangle([(40, 775), (1400, 930)], radius=10, fill=(17, 24, 39), outline=(31, 41, 55), width=2)
    draw.rounded_rectangle([(55, 785), (370, 811)], radius=6, fill=(131, 24, 67))
    draw.text((65, 793), "TIER 5: AI PROVIDERS, DATA & STORAGE", font=section_font, fill=(252, 231, 243))

    infra = [
        (60, 822, 315, "Free-Tier LLM Cloud Providers", ["• Groq Cloud (Llama-3-70B & 8B-Versatile)", "• Google AI Studio (Gemini 1.5 Flash Free)", "Offline Parametric Heuristic Fallback Engine"], (244, 114, 182)),
        (390, 822, 325, "Vector Storage & Lexical Search", ["• Pure-Python Numpy Cosine Vector Store", "• Okapi BM25 Lexical Inverted Index", "Optional Milvus 2.4.0 Container on Port 19530"], (56, 189, 248)),
        (730, 822, 330, "Profile & Session Persistence", ["• SQLite Database / Structured JSON Records", "• Cross-Session Concept Mastery Scores", "Adaptive Recommendation Knowledge Graph"], (251, 191, 36)),
        (1075, 822, 310, "File Storage Hierarchy", ["• data/uploads/ & data/plans/", "• data/rendered_videos/ & manifests/", "data/quizzes/, reports/ & profiles/"], (52, 211, 153))
    ]
    for (x, y, w, title, bullets, col) in infra:
        draw.rounded_rectangle([(x, y), (x+w, y+92)], radius=8, fill=(30, 41, 59), outline=(51, 65, 85), width=1)
        draw.text((x+12, y+10), title, font=card_title_font, fill=col)
        for i, b in enumerate(bullets):
            f_col = (203, 213, 225) if i < 2 else (100, 116, 139)
            f_font = card_body_font if i < 2 else card_foot_font
            draw.text((x+12, y+30 + i*18), b, font=f_font, fill=f_col)

    # Footer Info
    draw.text((40, 948), "AI Teacher Platform • Comprehensive 5-Tier Architecture • Zero-Cost Free-Tier APIs & Open-Source Local Pipelines", font=card_foot_font, fill=(100, 116, 139))
    draw.text((1200, 948), "AI Innovation Hackathon 2026", font=card_foot_font, fill=(100, 116, 139))

    img.save(output_png_path, "PNG")
    print(f"Generated PNG at: {output_png_path}")

if __name__ == "__main__":
    generate_svg("docs/architecture_diagram.svg")
    generate_png("docs/architecture_diagram.png")
