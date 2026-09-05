# Plan: Pyrender Avatar Service Tests & Integration

## Context
The `pyrender_avatar_service.py` was added to replace the Blender-based avatar rendering with a pure-Python off-screen renderer using `pyrender` and `trimesh`. The `video_stitcher.py` already imports and calls `pyrender_avatar_service.render_avatar_clip` for avatar segments.

## Goals
1. Install missing Python dependencies.
2. Add unit tests for the new renderer.
3. (Optional/Future) Add a phoneme-driven viseme mapper.
4. Update README/architecture docs.
5. Validate by running the test suite.

## Tasks

### 1. Install Dependencies
- Add `pyrender>=0.1.45`, `trimesh[easy]>=4.0.0`, and `pyglet` (for headless pyrender) to `backend/requirements.txt`.
- Run `pip install -r backend/requirements.txt` in the active virtualenv.

### 2. Add Unit Tests for `PyrenderAvatarService`
Create `backend/tests/test_pyrender_avatar_service.py` with tests covering:
- **Initialization**: verifies placeholder GLB creation when `default_teacher.glb` is absent; verifies mesh loads correctly.
- **Mouth deformation**: checks that `_apply_mouth_deformation` returns a mesh with modified vertices.
- **Clip generation**: renders a short avatar clip from a synthetic audio file (generated via `tts_service.synthesize_sync`) and asserts the output MP4 exists, has size > 5 MB, and duration matches audio within ±0.5s.
- **Branding consistency**: samples a frame and verifies the lower-third banner and teacher name are present.
- **Error fallback**: verifies graceful handling when ffmpeg is unavailable or returns non-zero (raises `RuntimeError`).

### 3. Update Existing Tests
- In `tests/test_video.py`, update the `generated_video_bundle` fixture to work with the new renderer (it already calls `video_stitcher`, which now uses pyrender).
- Ensure `test_photorealistic_avatar_and_speedup.py` does not fail due to missing `pyrender` imports; it should continue to test the original `AvatarService` independently.

### 4. Add Phoneme-Driven Viseme Mapper (Future)
Create `backend/app/services/phoneme_mapper.py`:
- Use `pymfa` or `gentle` aligner if available; otherwise implement a simple phoneme-to-viseme lookup table.
- Expose `get_visemes(audio_path, fps)` returning per-frame viseme IDs.
- Update `PyrenderAvatarService.render_avatar_clip` to accept an optional `visemes` array and drive mouth deformation via blend-shape or vertex offsets instead of RMS energy.

### 5. Update Documentation
- Update `README.md` under **R3: Hybrid Neural Video Pipeline** to mention the new `pyrender` off-screen renderer as the default avatar engine.
- Update `docs/architecture.md` if it references Blender or Wav2Lip as the primary avatar backend.

### 6. Validation
- Run `pytest backend/tests/test_pyrender_avatar_service.py -v`.
- Run `pytest backend/tests/test_video.py -v` (expect longer runtime due to video rendering).
- Run `pytest backend/tests/test_photorealistic_avatar_and_speedup.py -v` to confirm original avatar service is unaffected.
- Verify generated videos in `data/rendered_videos/` are under 5 MB and playable.

## Open Questions / Risks
- **Headless rendering**: `pyrender` may require `pyglet` with a headless EGL backend. If EGL is unavailable, we may need to switch to `osmesa` or render to PNG then encode with ffmpeg (already the plan).
- **Performance**: CPU rendering at 1280x720 is slower than the 2.5D PIL-based approach. If SLA (>20s per minute) is exceeded, consider lowering resolution or caching static frames.
- **Phoneme alignment**: `pymfa` / `gentle` are not in requirements yet; this task is deferred unless user confirms.
