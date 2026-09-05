"""
Avatar video generation for ApniHelp.

This module is a thin compatibility shim around ``AvatarService``, the
flat 2D illustrated teacher that is drawn directly with PIL
(no 3D model, no photograph, no portrait asset). The character is a
cartoon-style head with hair, eyes, eyebrows, nose, and a 5-viseme
mouth that is driven by the audio RMS envelope for lip-sync. The
output is a 1280x720 30 fps H.264 MP4 with audio baked in, sitting on
top of a branded ApniHelp background (gradient + lower-third banner
with the teacher name and lesson title + audio equalizer).

Earlier iterations of this service used:

* a 3D ``pyrender`` / ``trimesh`` teacher head (replaced because the
  face was either too dark or blown-out and there is no easy way to
  produce a friendly 3D character on a CPU-only build agent);
* a photorealistic portrait with PIL viseme compositing (replaced per
  product decision — we now use a flat illustrated character instead).

``video_stitcher.py`` continues to call
``pyrender_avatar_service.render_avatar_clip`` exactly as it did
before. All real rendering happens in
``AvatarService.generate_avatar_clip``, which paints one RGB24 frame
per timestep and pipes the raw stream to ffmpeg via stdin.
"""

import os
import subprocess
import numpy as np
from pathlib import Path
from typing import Optional

# ``PIL`` is only used here for the placeholder frame the shim exposes
# to legacy callers; the real rendering is done by ``AvatarService``.
from PIL import Image, ImageDraw, ImageFont

from backend.app.config import settings
from backend.app.services.avatar_service import AvatarService, avatar_service


# Public output resolution — kept as 1280x720 to match the rest of the
# pipeline (and the previous pyrender service API).
OUTPUT_WIDTH = 1280
OUTPUT_HEIGHT = 720


class PyrenderAvatarService:
    """Compatibility wrapper around the illustrated 2D teacher service.

    The public ``render_avatar_clip`` API matches the prior pyrender
    implementation so ``video_stitcher.py`` can call it unchanged, but
    internally it delegates to ``AvatarService.generate_avatar_clip``,
    which paints a friendly cartoon teacher (head, hair, eyes, eyebrows,
    nose, 5-viseme mouth) on top of a branded background.
    """

    def __init__(self, avatar_dir: Optional[Path] = None):
        self.avatar_dir = Path(avatar_dir) if avatar_dir else settings.avatar_dir
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = settings.ffmpeg_path
        self.width = OUTPUT_WIDTH
        self.height = OUTPUT_HEIGHT
        self.fps = 30

        # The real implementation lives in ``AvatarService``; ``self.mesh``
        # is preserved for older callers that probe for it.
        self._avatar_engine = avatar_service
        self._base_avatar = AvatarService()  # for envelope extraction
        self.mesh = None
        self.model_path = self.avatar_dir / "default_teacher.glb"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render_avatar_clip(
        self,
        audio_path: Path,
        output_path: Path,
        persona: str = "professor_alex",
        subject_title: str = "AI Teacher Lecture",
        teacher_name: str = "Prof. Alexander Vance",
    ) -> Path:
        """Render an illustrated teacher avatar clip synced to ``audio_path``.

        Delegates to ``AvatarService.generate_avatar_clip``, which paints
        a 2D cartoon teacher with a 5-viseme mouth driven by the audio
        RMS envelope. The output is a 1280x720 30 fps H.264 MP4 with
        audio baked in.
        """
        return self._avatar_engine.generate_avatar_clip(
            audio_path=Path(audio_path),
            output_path=Path(output_path),
            persona=persona,
            subject_title=subject_title,
            teacher_name=teacher_name,
        )


# Module-level singleton used by video_stitcher.
pyrender_avatar_service = PyrenderAvatarService()
