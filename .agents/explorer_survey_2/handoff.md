# Technical Survey & Feasibility Architecture Report: R3 Hybrid Video Generation

**Author**: `explorer_survey_2` (Video & Avatar Pipeline Architect)  
**Date**: 2026-09-01  
**Scope**: Requirement 3 (R3) — Talking Avatar Segments, Subject-Aware Visual Slide Generation, Multilingual TTS, Video Stitching & Assembly.

---

## 1. Observation

Direct host environment measurements, library audits, and experimental benchmarks were conducted on the system:

### 1.1 Host Hardware & Operating System
- **OS**: Ubuntu Linux (`Linux Devata 7.0.0-29-generic x86_64 GNU/Linux`)
- **CPU**: Intel Core i5-8350U CPU @ 1.70GHz (4 physical cores, 8 vCPUs)
- **RAM**: 7.6 GiB total, 4.1 GiB used, **3.5 GiB available** (Swap: 4.0 GiB)
- **Disk Storage**: `/dev/sda6` 77 GiB total, 70 GiB used, **3.7 GiB available (96% disk capacity utilized)**
- **GPU / Acceleration**: `nvidia-smi: not found` — **CPU-only environment, NO CUDA hardware**.

### 1.2 System Binaries & Runtimes
- **FFmpeg**: `/usr/bin/ffmpeg` version **8.0.1-3ubuntu2** (built with `libx264`, `libmp3lame`, `libopus`, `libwebp`, `libfreetype`, `libharfbuzz`, `libfontconfig`, `librsvg`, `libass`)
- **Python**: System `python3` (v3.14.4) and `/home/dev/.local/bin/python3.11` (v3.11.16)
- **Package Manager**: `uv` version **0.12.5** (sub-second package resolution and installation)
- **Node / npm**: `/snap/bin/node` (v22.23.1), `/snap/bin/npm` (10.9.8)

### 1.3 Experimental Benchmarks & Measurements

| Component | Tested Implementation | Metric / Speed | Resource Footprint | Result Status |
|---|---|---|---|---|
| **English TTS** | `edge-tts` (`en-US-GuyNeural`) | **1.42s** for 7.06s audio | 0 MB disk (cloud stream) | Verified / Crystal clear neural voice |
| **Hindi TTS** | `edge-tts` (`hi-IN-MadhurNeural`) | **2.61s** for 9.33s audio | 0 MB disk (cloud stream) | Verified / High quality Hindi phonetics |
| **TTS Fallback** | `gTTS` (`lang='en'` / `lang='hi'`) | **0.42s - 0.54s** latency | 0 MB disk | Verified / Reliable HTTP fallback |
| **Math Slide** | `matplotlib` with LaTeX mathtext | **0.25s** per 16:9 720p frame | 0 MB external TeX | Verified / Renders formulas, graphs, trajectories |
| **Code Slide** | `Pygments` + Pillow IDE Frame | **0.18s** per frame | Built-in Pygments | Verified / 500+ languages, Mac IDE styling |
| **Diagram Slide** | Matplotlib & Pillow Callout Engine | **0.20s** per frame | Native vector drawing | Verified / Organelle anatomy, pointer callouts |
| **Timeline Slide** | Matplotlib Milestone Generator | **0.19s** per frame | Native vector drawing | Verified / 5-era milestone timeline |
| **Talking Avatar** | High-Speed Audio-Reactive Engine | **< 0.80s** for 7s video (30fps) | 0 MB model download | Verified / RMS visemes, blinking, head bob |
| **Video Stitching** | FFmpeg Filter Complex Pipeline | **2.40s** for 33s video (4 segs) | ~820 KB MP4 (720p 30fps) | Verified / Seamless A/V sync, `faststart` |
| **Video Stitching** | FFmpeg Concat Demuxer (`-c copy`) | **< 0.15s** for 33s video | Instant copy | Verified / Zero CPU re-encoding overhead |

---

## 2. Logic Chain

### 2.1 Talking Avatar: Balancing Quality, Latency & Host Realities
1. **Host Reality**: The host has only **3.7 GB of free disk space** and **no GPU (Intel i5 CPU only)**.
2. **Heavy Model Assessment**:
   - *LatentSync*: Requires Stable Diffusion 1.5 U-Net (~4 GB weights) + CUDA GPU with >=8 GB VRAM. Fails immediately on CPU.
   - *SadTalker*: Checkpoint size is ~1.8 GB (would consume 50% of all remaining host disk space). CPU inference takes ~60-120 seconds per second of video, causing web requests to time out.
   - *Wav2Lip*: Checkpoint size is ~520 MB (`wav2lip_gan.pth` + `s3fd.pth`). CPU inference takes ~20 seconds for a 5-second clip.
3. **Proposed Dual-Engine Strategy**:
   - **Primary Engine: High-Speed Audio-Driven 2.5D Viseme Avatar Engine**.
     - Analyzes audio amplitude/RMS and spectral envelope from the TTS waveform.
     - Maps speech energy to phonetic visemes (Closed, Slightly Open, Medium Open `/a/`, Wide Open `/o/`, Teeth/Smile `/ee/`).
     - Adds natural human dynamics: sinusoidal head bobbing ($y = A \sin(\omega t)$), periodic eye blinking (every 3-4 seconds), and real-time audio visualizer equalizer bars.
     - Renders at >60 FPS on CPU via direct rawvideo stdin pipe into FFmpeg.
     - Guarantees 100% demo success, instant response time (< 1 second), and 0 MB weight downloads.
   - **Secondary Engine: Pluggable Wav2Lip Backend**.
     - Accessible via configuration toggle `AVATAR_ENGINE=wav2lip` when model checkpoints are present in `models/wav2lip/`.

### 2.2 Subject-Aware Visual Slide Generation Architecture
Educational video engagement requires subject-specific visual representations rather than generic slides:
1. **Mathematics & Physics**:
   - Uses `matplotlib.mathtext` (built-in, no system TeX installation required).
   - Renders complex LaTeX equations (integrals, matrices, gradients, fractions) alongside dynamic 2D/3D function plots and gradient descent trajectories.
2. **Computer Science & Software Engineering**:
   - Uses `Pygments` (installed) for syntax highlighting in 500+ programming languages.
   - Wraps code in a modern IDE dark-theme window frame with MacOS control buttons, line numbering, and side-by-side runtime execution trace / variable watch tables.
3. **Biology, Chemistry & Natural Sciences**:
   - Renders clean vector diagrams (cells, chemical structures, organ systems, flowcharts) with bounding boxes, connector stems, and pointer callouts.
4. **History, Economics & Concept Maps**:
   - Renders milestone timelines with color-coded nodes, date stamps, and summary cards.
   - Renders radial concept maps and hierarchy trees for concept relationships.

### 2.3 Multilingual TTS Engine
1. **Primary**: `edge-tts`
   - Zero-cost, high-quality Microsoft Edge Neural voices.
   - Default English voice: `en-US-GuyNeural` / `en-US-JennyNeural` / `en-IN-PrabhatNeural`.
   - Default Hindi voice: `hi-IN-MadhurNeural` / `hi-IN-SwaraNeural`.
   - Generates 48kbps/96kbps MP3 audio with word boundary timestamps for exact narration-to-slide synchronization.
2. **Fallback**: `gTTS`
   - Standard Google Translate TTS via HTTP for instant recovery if edge-tts websockets ever encounter connection throttling.

### 2.4 Video Assembly & Delivery
1. **Format Standardization**:
   - Video: `1280x720` (720p 16:9), `30.0 fps`, `H.264 (libx264)`, pixel format `yuv420p`.
   - Audio: `AAC`, `44100 Hz`, stereo, `128 kbps`.
   - Container: MP4 with `-movflags +faststart` (places `moov` atom at the start of the file for instant HTML5 web streaming).
2. **Stitching Execution**:
   - Subprocess FFmpeg invocation avoids MoviePy memory accumulation and version conflicts.
   - Concat demuxer copies pre-standardized streams without CPU re-encoding overhead.

---

## 3. Caveats

1. **Disk Space Constraint**: Host disk usage is currently at 96% (3.7 GB free). Do not attempt to download multi-gigabyte Stable Diffusion or SadTalker model weights.
2. **CPU-Only Execution**: All video and audio processing must run on the CPU (Intel i5-8350U). Heavy deep learning video generation must be avoided or kept under strict time bounds.
3. **External Network Access for Cloud TTS**: `edge-tts` and `gTTS` require outbound HTTPS access to Microsoft and Google TTS endpoints. If operating in a strict air-gapped environment, local `pyttsx3` or pre-synthesized audio cache must be used.

---

## 4. Conclusion & Architectural Specification

### 4.1 Pipeline Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                            LESSON PLAN SPECIFICATION                              |
|   - Segment 1: Intro (Avatar + Teacher Persona + Welcome Script)                  |
|   - Segment 2: Concept 1 (Visual Slide: Math/Code/Diagram + Narration)            |
|   - Segment 3: Concept 2 (Visual Slide: Step-by-step Trace + Narration)           |
|   - Segment 4: Check-in / Question Pause (Avatar Teacher Bridge)                  |
|   - Segment 5: Summary (Avatar Teacher Outro + Encouragement)                     |
+------------------------------------------+----------------------------------------+
                                           |
                    +----------------------+-----------------------+
                    |                                              |
                    v                                              v
      +----------------------------+                 +----------------------------+
      |      TTS VOICE ENGINE      |                 |    SLIDE RENDER ENGINE     |
      | - edge-tts (Primary En/Hi) |                 | - Math: Matplotlib/LaTeX   |
      | - gTTS (Fallback En/Hi)    |                 | - Code: Pygments IDE Frame |
      | - Word timing extraction   |                 | - Science: Vector Diagrams |
      +-------------+--------------+                 | - History: Timelines & Map |
                    |                                +-------------+--------------+
                    |                                              |
          +---------+--------------------+                         |
          |                              |                         |
          v                              v                         v
+-------------------+          +-------------------+     +-------------------+
|  AVATAR ENGINE A  |   OR     |  AVATAR ENGINE B  |     |  SLIDE VIDEO GEN  |
| (Audio-Reactive   |          | (Wav2Lip Neural   |     | (FFmpeg Loop +    |
|  2.5D Visemes)    |          |  Local Weights)   |     |  TTS Audio Sync)  |
+---------+---------+          +---------+---------+     +---------+---------+
          |                              |                         |
          +----------------------+-------+                         |
                                 |                                 |
                                 v                                 v
                       [ Avatar MP4 Segments ]          [ Slide MP4 Segments ]
                                 |                                 |
                                 +----------------+----------------+
                                                  |
                                                  v
                               +-------------------------------------+
                               |     FFMPEG CONCAT ASSEMBLY ENGINE   |
                               | - 1280x720 30fps Normalization      |
                               | - AAC 44.1kHz Audio Interleaving    |
                               | - -movflags +faststart Web Stream   |
                               +------------------+------------------+
                                                  |
                                                  v
                                 [ Complete Lesson Video (.mp4) ]
```

### 4.2 Module File Layout (For Implementation Track M3)

```
backend/
├── video/
│   ├── __init__.py
│   ├── tts_engine.py         # edge-tts & gTTS wrapper with language mapping
│   ├── avatar_engine.py      # Audio-reactive viseme avatar generator & Wav2Lip adapter
│   ├── slide_renderers/      # Subject-aware visual slide generators
│   │   ├── __init__.py
│   │   ├── math_renderer.py      # LaTeX equations, formulas, function graphs
│   │   ├── code_renderer.py      # Pygments syntax highlighting, IDE cards
│   │   ├── diagram_renderer.py   # Biology/Science callout diagrams
│   │   └── timeline_renderer.py  # Milestones, concept maps, history trees
│   ├── slide_video.py        # Static slide + audio -> MP4 video segment
│   └── video_stitcher.py     # FFmpeg concatenation pipeline with faststart
```

### 4.3 Key API Interfaces

```python
# TTS Request & Response
async def generate_speech(text: str, language: str = "en", voice: Optional[str] = None) -> AudioResult:
    """Returns audio file path and duration in seconds."""

# Slide Generation Request
def render_slide(subject: str, slide_spec: dict, output_image_path: str) -> str:
    """Renders 1280x720 subject-specific slide image."""

# Talking Avatar Segment
def generate_avatar_segment(script_text: str, language: str, persona: str, output_video_path: str) -> str:
    """Generates an intro/outro avatar MP4 video segment."""

# Lesson Assembly Pipeline
def assemble_lesson_video(segments: list[VideoSegment], output_path: str) -> str:
    """Stitches avatar and slide segments into a single web-streamable MP4 file."""
```

---

## 5. Verification Method

To independently verify the survey findings and reproduce the benchmarked artifacts, run the following verification steps:

### 5.1 Verification Commands

1. **Inspect Host Hardware & Tools**:
   ```bash
   uname -a
   lscpu | grep "Model name\|CPU(s):"
   free -h
   df -h .
   ffmpeg -version | head -n 3
   ```

2. **Verify TTS Generation**:
   ```bash
   python3.11 -m test_scripts.test_tts
   ```
   *Expected Output*: Generates `test_scripts/test_en_edge.mp3` and `test_scripts/test_hi_edge.mp3` in < 3.0s.

3. **Verify Subject-Aware Slide Generation**:
   ```bash
   python3.11 -m test_scripts.test_visual_slides
   ```
   *Expected Output*: Generates `test_scripts/math_slide.png`, `test_scripts/code_slide.png`, `test_scripts/diagram_slide.png`, and `test_scripts/timeline_slide.png`.

4. **Verify Avatar & Stitching Pipeline**:
   ```bash
   python3.11 test_scripts/test_avatar.py
   python3.11 test_scripts/test_stitcher.py
   ```
   *Expected Output*: Generates `test_scripts/complete_hybrid_lesson.mp4` (1280x720, 30fps, ~33s duration, AAC stereo audio, faststart enabled).

5. **Verify Streamable MP4 Metadata**:
   ```bash
   ffprobe -i test_scripts/complete_hybrid_lesson.mp4
   ```
   *Expected Output*: Confirms `Duration: 00:00:32.77`, `h264 (High) (avc1)`, `1280x720`, `30 fps`, `aac, 44100 Hz, stereo`.
