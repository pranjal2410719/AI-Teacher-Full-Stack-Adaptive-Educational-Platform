# Dispatch: explorer_r3_video_avatar

## Objective
Investigate the video generation pipeline and avatar rendering in the current codebase to satisfy:
- **R1. Video generation performance**: The system must generate a video in ≤20 seconds of processing for each minute of final video length (e.g., a 5-minute video ≤100 seconds, 10-minute ≤200 seconds).
- **R4. AI teacher avatar**: The video presenter must be a photorealistic human-like AI teacher image generated via an image model, not a cartoon illustration, synced with narration.

## Working Directory
`/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar`

## Scope & Tasks
1. Read `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md` (lines 81-120 specifically for the new ApniHelp requirements).
2. Inspect `backend/src/video/`, avatar generation logic, slide rendering, TTS generation (`backend/src/video/tts.py` or similar), FFmpeg video assembly, and any benchmark or test scripts.
3. Measure/analyze current processing time per minute of video output. Identify where the time is spent (TTS synthesis, frame-by-frame slide rendering, viseme/avatar overlay, FFmpeg encoding, etc.).
4. Propose concrete optimization strategies to ensure generation speed is strictly ≤20 seconds processing per 60 seconds of video output (e.g., fast FFmpeg encoding flags like ultrafast/veryfast presets, optimized resolution/fps, multiprocessing/threading for slide rendering, vectorized viseme compositing, direct video filter graphs).
5. Inspect the current avatar implementation. How is the avatar image loaded, rendered, or composited? Is it a cartoon/vector avatar currently? Where should the photorealistic human-like AI teacher image be stored (e.g., in assets/avatar) and how should visemes/lip-sync and eye blinking or speech animation be rendered with photorealism? Note that `generate_image` or high-quality AI-generated teacher assets can be used.
6. Write a comprehensive report in your working directory at `analysis.md` and a structured `handoff.md`.

## 2026-09-04T17:46:18Z
You are explorer_r3_video_avatar, a specialized exploration agent.
Your working directory is: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar
Please read your assignment file: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/DISPATCH.md
MANDATORY: Read /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md before starting work. Do NOT summarize or filter it — read the authoritative user request directly, especially the ApniHelp requirements (lines 81-120).

Your investigation focus:
1. Video generation performance (R1): current speed, bottlenecks, and concrete architectural optimizations so that video processing time is strictly <= 20 seconds per minute of final video length (for 5 min and 10 min videos).
2. AI teacher avatar (R4): investigate how the avatar is currently rendered, replace cartoon/vector elements with a photorealistic human-like AI teacher image generated via image model, and ensure visemes/lip-sync and speech animation are cleanly synchronized.

Deliver your findings in /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/analysis.md and write a structured handoff.md. Report back with send_message when done.
