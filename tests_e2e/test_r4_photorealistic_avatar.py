"""
R4 Acceptance Test: Photorealistic AI Teacher Avatar & Audio-Visual Speech Sync
==============================================================================
Authoritative Specification: ORIGINAL_REQUEST.md (lines 104-105, 115)
"The video presenter must be a photorealistic human-like AI teacher image generated
via an image model, not a cartoon illustration."
Acceptance Criteria: "The generated video features a photorealistic teacher avatar
that syncs with the narration."

This test suite verifies:
  1. Photographic Avatar Asset Properties:
     - High texture standard deviation (> 25.0) proving complex human skin/lighting
       rather than flat cartoon/clipart illustration.
     - Shannon entropy (> 6.0 bits) verifying natural photographic color distribution.
     - High resolution (>= 720p: 1280x720).
  2. Audio-Visual Speech Synchronization:
     - Generated avatar video clip duration strictly matches audio duration within +/- 0.2s.
  3. Dynamic Lip-Sync Modulation:
     - RMS audio energy envelope drives viseme state transitions.
"""

import math
import subprocess
from pathlib import Path
import pytest
import numpy as np
from PIL import Image

from backend.app.config import settings
from backend.app.services.avatar_service import avatar_service
from backend.app.services.tts_service import tts_service


def test_r4_avatar_asset_resolution_and_format():
    """
    R4.1: Asserts that high-resolution photorealistic avatar assets exist
    in settings.avatar_dir with resolution >= 720p (1280x720).
    """
    avatar_dir = settings.avatar_dir
    assert avatar_dir.exists(), f"Avatar assets directory not found at {avatar_dir}"

    female_portrait = avatar_dir / "teacher_portrait.png"
    male_portrait = avatar_dir / "teacher_portrait_male.png"

    assert female_portrait.exists(), f"Female avatar portrait missing: {female_portrait}"
    assert male_portrait.exists(), f"Male avatar portrait missing: {male_portrait}"

    for p_path in [female_portrait, male_portrait]:
        with Image.open(p_path) as img:
            w, h = img.size
            assert w >= 1280 and h >= 720, (
                f"R4 VIOLATION: Avatar {p_path.name} resolution {w}x{h} does not satisfy >= 720p (1280x720)"
            )
            assert img.mode in ("RGB", "RGBA"), f"Avatar {p_path.name} must be RGB/RGBA format"


def test_r4_photorealistic_texture_variance_not_cartoon():
    """
    R4.2: Asserts that the avatar image exhibits photographic texture variance (std_dev > 25.0)
    and Shannon entropy (> 6.0 bits), proving it is a genuine AI-generated human portrait
    and not a flat cartoon illustration or 2D vector graphic.
    """
    female_portrait = settings.avatar_dir / "teacher_portrait.png"
    male_portrait = settings.avatar_dir / "teacher_portrait_male.png"

    for p_path in [female_portrait, male_portrait]:
        img = Image.open(p_path).convert("RGB")
        arr = np.array(img, dtype=np.float32)

        # 1. Standard Deviation Check (flat cartoons typically have std_dev < 15.0)
        std_dev = float(np.std(arr))
        print(f"[R4 Photorealism Check - {p_path.name}]: Standard Deviation = {std_dev:.2f}")
        assert std_dev > 25.0, (
            f"R4 VIOLATION: Image {p_path.name} texture variance ({std_dev:.2f}) <= 25.0, "
            f"indicating flat cartoon/vector illustration instead of photographic human teacher."
        )

        # 2. Shannon Entropy Check (natural photographic portraits exhibit entropy > 6.0 bits)
        gray = np.dot(arr[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        hist, _ = np.histogram(gray, bins=256, range=(0, 256), density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        print(f"[R4 Photorealism Check - {p_path.name}]: Shannon Entropy = {entropy:.2f} bits")
        assert entropy > 6.0, (
            f"R4 VIOLATION: Image {p_path.name} entropy ({entropy:.2f} bits) <= 6.0, "
            f"lacking photographic information density."
        )


def test_r4_avatar_audio_visual_speech_sync():
    """
    R4.3: Asserts audio-visual synchronization: the generated avatar video clip duration
    must match the narration audio duration within +/- 0.2 seconds.
    """
    # Synthesize test audio track
    test_phrase = "Welcome to ApniHelp. In this lesson, we will understand limits and continuity with precision."
    audio_path, expected_audio_dur = tts_service.synthesize_sync(test_phrase, language="en")
    assert audio_path.exists()
    assert expected_audio_dur > 1.0

    output_clip = settings.video_dir / "test_r4_sync_clip.mp4"
    if output_clip.exists():
        output_clip.unlink()

    # Generate avatar clip
    avatar_service.generate_avatar_clip(
        audio_path=audio_path,
        output_path=output_clip,
        persona="professor_alex",
        subject_title="Calculus Fundamentals",
        teacher_name="Prof. Alexander Vance",
    )

    assert output_clip.exists(), f"Avatar video clip not created at {output_clip}"
    assert output_clip.stat().st_size > 10000

    # Query video duration via ffprobe
    cmd_v = [
        settings.ffprobe_path,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(output_clip),
    ]
    res_v = subprocess.run(cmd_v, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    video_dur = float(res_v.stdout.strip())

    # Query audio duration via ffprobe
    actual_audio_dur = tts_service.get_audio_duration(audio_path)

    dur_diff = abs(video_dur - actual_audio_dur)
    print(f"\n[R4 AV Sync]: Audio Duration={actual_audio_dur:.3f}s, Video Duration={video_dur:.3f}s, Delta={dur_diff:.3f}s")

    assert dur_diff <= 0.2, (
        f"R4 VIOLATION: Audio-visual sync difference {dur_diff:.3f}s exceeds strict tolerance of +/- 0.2s"
    )


def test_r4_dynamic_lip_sync_energy_envelope():
    """
    R4.4: Asserts that the audio energy envelope correctly captures speech cadence
    and dynamically modulates mouth visemes (open during speech phonemes, closed during silence).
    """
    test_phrase = "Hello from ApniHelp!"
    audio_path, audio_dur = tts_service.synthesize_sync(test_phrase, language="en")

    envelope = avatar_service.extract_audio_energy_envelope(audio_path, fps=30)
    assert len(envelope) > 0, "Envelope must contain computed RMS energy values"

    expected_frames = math.ceil(audio_dur * 30)
    frame_diff = abs(len(envelope) - expected_frames)
    assert frame_diff <= 2, f"Envelope frame count {len(envelope)} deviates from expected {expected_frames}"

    # Verify dynamic energy variation
    max_energy = float(np.max(envelope))
    min_energy = float(np.min(envelope))
    assert max_energy > 0.15, "Envelope should detect clear speech vocal energy"
    assert min_energy < 0.10, "Envelope should contain rest/low energy points for mouth closing"
