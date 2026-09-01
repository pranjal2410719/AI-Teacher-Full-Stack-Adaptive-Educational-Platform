"""
High-Speed Audio-Driven 2.5D Viseme Talking Avatar Service.
Synthesizes speech-synchronized talking head video clips from audio waveforms
with dynamic viseme phonetics, natural eye blinks, sinusoidal head bobbing,
and real-time equalizer visualizers. Includes pluggable Wav2Lip CLI backend.
"""

import os
import math
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.config import settings

logger = logging.getLogger(__name__)


class AvatarService:
    """High-speed 2.5D Audio-Reactive Viseme Avatar Generator & Wav2Lip Adapter."""

    def __init__(self, avatar_dir: Optional[Path] = None):
        self.avatar_dir = Path(avatar_dir) if avatar_dir else settings.avatar_dir
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = settings.ffmpeg_path
        self.ffprobe_path = settings.ffprobe_path
        self.width = 1280
        self.height = 720
        self.fps = 30

    def extract_audio_energy_envelope(self, audio_path: Path, fps: int = 30) -> np.ndarray:
        """
        Decodes audio into 16kHz mono PCM and computes per-frame RMS energy.
        Returns normalized 1D numpy array of length = total_frames.
        """
        sample_rate = 16000
        cmd = [
            self.ffmpeg_path,
            "-v", "error",
            "-i", str(audio_path),
            "-f", "s16le",
            "-ac", "1",
            "-ar", str(sample_rate),
            "pipe:1",
        ]
        try:
            raw_pcm = subprocess.check_output(cmd)
            audio_samples = np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32)
        except Exception as e:
            logger.warning(f"Audio PCM extraction failed for {audio_path}: {e}, using synthetic envelope.")
            # Default fallback envelope: 3-second gentle pulse
            total_samples = sample_rate * 3
            audio_samples = np.zeros(total_samples, dtype=np.float32)

        total_audio_sec = len(audio_samples) / float(sample_rate)
        total_frames = max(1, int(math.ceil(total_audio_sec * fps)))
        samples_per_frame = int(sample_rate / fps)

        envelope = np.zeros(total_frames, dtype=np.float32)
        for f in range(total_frames):
            start = f * samples_per_frame
            end = min(len(audio_samples), start + samples_per_frame)
            if start < len(audio_samples) and end > start:
                chunk = audio_samples[start:end]
                rms = np.sqrt(np.mean(chunk ** 2))
                envelope[f] = rms

        # Normalize envelope to [0.0, 1.0]
        max_val = np.max(envelope) if len(envelope) > 0 else 0.0
        if max_val > 100.0:
            envelope = envelope / max_val
        else:
            # Low volume or empty: apply modest scaling
            envelope = np.clip(envelope / 2000.0, 0.0, 1.0)

        # Smooth envelope with exponential moving average (alpha=0.4)
        smoothed = np.zeros_like(envelope)
        curr = 0.0
        for i, val in enumerate(envelope):
            curr = 0.4 * val + 0.6 * curr
            smoothed[i] = curr

        return smoothed

    def render_avatar_frame(
        self,
        frame_idx: int,
        total_frames: int,
        energy: float,
        persona: str = "professor_alex",
        subject_title: str = "AI Teaching Lecture",
        teacher_name: str = "Prof. Alexander Vance",
    ) -> Image.Image:
        """
        Renders a single 1280x720 RGB frame for the avatar character
        with audio-driven mouth viseme, blinking eyes, subtle head bobbing,
        and audio equalizer HUD.
        """
        t = frame_idx / float(self.fps)

        # 1. Base Canvas & Academic Background Gradient
        img = Image.new("RGB", (self.width, self.height), (18, 22, 32))
        draw = ImageDraw.Draw(img)

        # Draw sleek gradient background & subtle classroom grid/glow
        for y in range(0, self.height, 4):
            ratio = y / float(self.height)
            r = int(18 + 12 * ratio)
            g = int(24 + 18 * ratio)
            b = int(38 + 24 * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b), width=4)

        # Studio backdrop glow behind avatar
        glow_center = (640, 360)
        draw.ellipse([glow_center[0] - 380, glow_center[1] - 300, glow_center[0] + 380, glow_center[1] + 340], fill=(28, 38, 62))
        draw.ellipse([glow_center[0] - 280, glow_center[1] - 220, glow_center[0] + 280, glow_center[1] + 240], fill=(36, 50, 80))

        # 2. Sinusoidal Head & Torso Bobbing / Breathing
        head_bob_y = int(3.5 * math.sin(2.0 * math.pi * 0.55 * t))
        head_bob_x = int(1.5 * math.sin(2.0 * math.pi * 0.28 * t))

        # Avatar Center Coordinates
        cx = 640 + head_bob_x
        cy = 340 + head_bob_y

        # 3. Torso & Teacher Attire (Dark Navy Blazer, Crisp Shirt, Tie)
        # Shoulders & Body
        torso_box = [cx - 240, cy + 180, cx + 240, cy + 480]
        draw.polygon([
            (cx - 240, 720),
            (cx - 210, cy + 200),
            (cx - 110, cy + 150),
            (cx + 110, cy + 150),
            (cx + 210, cy + 200),
            (cx + 240, 720),
        ], fill=(25, 32, 48))

        # Shirt Collar & V-Neck
        draw.polygon([
            (cx - 70, cy + 150),
            (cx, cy + 260),
            (cx + 70, cy + 150),
        ], fill=(240, 244, 250))

        # Necktie
        draw.polygon([
            (cx - 16, cy + 180),
            (cx + 16, cy + 180),
            (cx + 24, cy + 340),
            (cx, cy + 380),
            (cx - 24, cy + 340),
        ], fill=(180, 45, 55))
        # Tie knot
        draw.polygon([
            (cx - 18, cy + 175),
            (cx + 18, cy + 175),
            (cx + 14, cy + 200),
            (cx - 14, cy + 200),
        ], fill=(210, 50, 60))

        # Blazer Lapels
        draw.polygon([
            (cx - 110, cy + 150),
            (cx - 50, cy + 260),
            (cx - 85, cy + 400),
            (cx - 160, cy + 300),
        ], fill=(35, 45, 68))
        draw.polygon([
            (cx + 110, cy + 150),
            (cx + 50, cy + 260),
            (cx + 85, cy + 400),
            (cx + 160, cy + 300),
        ], fill=(35, 45, 68))

        # 4. Neck
        draw.rectangle([cx - 45, cy + 80, cx + 45, cy + 165], fill=(235, 192, 168))
        # Neck shadow
        draw.ellipse([cx - 45, cy + 135, cx + 45, cy + 175], fill=(215, 170, 145))

        # 5. Head & Facial Base
        head_radius_x = 110
        head_radius_y = 135
        draw.ellipse([cx - head_radius_x, cy - head_radius_y, cx + head_radius_x, cy + head_radius_y], fill=(245, 205, 180))

        # 6. Hair & Hairstyle
        hair_color = (48, 34, 28)
        draw.ellipse([cx - 120, cy - head_radius_y - 25, cx + 120, cy - 20], fill=hair_color)
        draw.polygon([
            (cx - 120, cy - 40),
            (cx - 115, cy + 10),
            (cx - 95, cy - 30),
            (cx - 60, cy - 100),
            (cx + 60, cy - 100),
            (cx + 95, cy - 30),
            (cx + 115, cy + 10),
            (cx + 120, cy - 40),
        ], fill=hair_color)

        # 7. Eyebrows (Dynamic expressiveness)
        brow_y = cy - 42
        brow_lift = int(energy * 4.0)
        draw.line([(cx - 75, brow_y - brow_lift), (cx - 25, brow_y - brow_lift - 4)], fill=(40, 28, 22), width=5)
        draw.line([(cx + 25, brow_y - brow_lift - 4), (cx + 75, brow_y - brow_lift)], fill=(40, 28, 22), width=5)

        # 8. Eyes & Natural Periodic Blinking
        # Blink every ~3.2 seconds for 3 frames
        blink_period_frames = 96  # ~3.2s @ 30fps
        is_blinking = (frame_idx % blink_period_frames) < 3

        eye_y = cy - 15
        if is_blinking:
            # Closed eyelids (curved arc)
            draw.arc([cx - 70, eye_y - 8, cx - 30, eye_y + 8], start=0, end=180, fill=(70, 50, 40), width=4)
            draw.arc([cx + 30, eye_y - 8, cx + 70, eye_y + 8], start=0, end=180, fill=(70, 50, 40), width=4)
        else:
            # Eye Sclera (White)
            draw.ellipse([cx - 70, eye_y - 14, cx - 30, eye_y + 14], fill=(255, 255, 255))
            draw.ellipse([cx + 30, eye_y - 14, cx + 70, eye_y + 14], fill=(255, 255, 255))
            # Irises (Deep Blue / Hazel)
            draw.ellipse([cx - 56, eye_y - 10, cx - 44, eye_y + 10], fill=(42, 85, 135))
            draw.ellipse([cx + 44, eye_y - 10, cx + 56, eye_y + 10], fill=(42, 85, 135))
            # Pupils (Black)
            draw.ellipse([cx - 53, eye_y - 6, cx - 47, eye_y + 6], fill=(15, 15, 20))
            draw.ellipse([cx + 47, eye_y - 6, cx + 53, eye_y + 6], fill=(15, 15, 20))
            # Specular light highlight
            draw.ellipse([cx - 54, eye_y - 8, cx - 51, eye_y - 4], fill=(255, 255, 255))
            draw.ellipse([cx + 46, eye_y - 8, cx + 49, eye_y - 4], fill=(255, 255, 255))

        # Academic Glasses (Gold / Silver Wireframes)
        draw.ellipse([cx - 78, eye_y - 20, cx - 22, eye_y + 20], outline=(210, 175, 95), width=3)
        draw.ellipse([cx + 22, eye_y - 20, cx + 78, eye_y + 20], outline=(210, 175, 95), width=3)
        draw.line([(cx - 22, eye_y - 3), (cx + 22, eye_y - 3)], fill=(210, 175, 95), width=3)
        draw.line([(cx - 78, eye_y - 5), (cx - 105, eye_y - 10)], fill=(210, 175, 95), width=2)
        draw.line([(cx + 78, eye_y - 5), (cx + 105, eye_y - 10)], fill=(210, 175, 95), width=2)

        # 9. Nose
        draw.line([(cx, cy - 10), (cx - 6, cy + 28)], fill=(215, 170, 145), width=3)
        draw.line([(cx - 6, cy + 28), (cx + 6, cy + 28)], fill=(215, 170, 145), width=3)

        # 10. Dynamic Viseme Phonetic Mouth Opening
        mouth_cx = cx
        mouth_cy = cy + 65

        # Determine viseme parameters from normalized energy envelope
        if energy < 0.08:
            # Viseme 0: Closed / Resting Mouth (Subtle gentle smile)
            draw.arc([mouth_cx - 28, mouth_cy - 10, mouth_cx + 28, mouth_cy + 10], start=15, end=165, fill=(185, 75, 80), width=4)
        elif energy < 0.28:
            # Viseme 1: Slightly Open (ah_small / m-b-p transition)
            open_h = int(6 + 10 * ((energy - 0.08) / 0.20))
            draw.ellipse([mouth_cx - 24, mouth_cy - open_h // 2, mouth_cx + 24, mouth_cy + open_h // 2], fill=(130, 30, 40))
            draw.rectangle([mouth_cx - 14, mouth_cy - open_h // 2, mouth_cx + 14, mouth_cy - open_h // 2 + 3], fill=(245, 245, 245))
        elif energy < 0.58:
            # Viseme 2: Medium Open (aa_med / conversational vowel)
            open_h = int(14 + 14 * ((energy - 0.28) / 0.30))
            draw.ellipse([mouth_cx - 28, mouth_cy - open_h // 2, mouth_cx + 28, mouth_cy + open_h // 2], fill=(110, 20, 30))
            # Upper teeth
            draw.rectangle([mouth_cx - 18, mouth_cy - open_h // 2, mouth_cx + 18, mouth_cy - open_h // 2 + 5], fill=(250, 250, 250))
            # Tongue
            draw.ellipse([mouth_cx - 14, mouth_cy + open_h // 2 - 8, mouth_cx + 14, mouth_cy + open_h // 2], fill=(210, 85, 95))
        elif energy < 0.78:
            # Viseme 4: Wide Grin / Phonetic 'EE'
            open_h = 16
            draw.ellipse([mouth_cx - 38, mouth_cy - open_h // 2, mouth_cx + 38, mouth_cy + open_h // 2], fill=(110, 20, 30))
            draw.rectangle([mouth_cx - 26, mouth_cy - open_h // 2, mouth_cx + 26, mouth_cy - open_h // 2 + 4], fill=(250, 250, 250))
        else:
            # Viseme 3: Wide Open 'OH' / Emphasis
            open_h = int(26 + 12 * (energy - 0.78))
            draw.ellipse([mouth_cx - 24, mouth_cy - open_h // 2, mouth_cx + 24, mouth_cy + open_h // 2], fill=(90, 15, 25))
            # Upper teeth
            draw.rectangle([mouth_cx - 14, mouth_cy - open_h // 2, mouth_cx + 14, mouth_cy - open_h // 2 + 4], fill=(250, 250, 250))
            # Tongue
            draw.ellipse([mouth_cx - 12, mouth_cy + open_h // 2 - 10, mouth_cx + 12, mouth_cy + open_h // 2], fill=(215, 85, 95))

        # 11. Studio HUD: Audio Equalizer Wave Visualizer Bars
        eq_x = 980
        eq_y = 660
        num_bars = 16
        bar_width = 12
        bar_gap = 5
        draw.rounded_rectangle([eq_x - 20, eq_y - 60, eq_x + num_bars * (bar_width + bar_gap) + 15, eq_y + 20], radius=8, fill=(15, 20, 30, 200), outline=(45, 60, 90), width=1)
        
        for b in range(num_bars):
            # Dynamic bar height driven by energy + harmonic frequency modulation
            harmonic_mod = 0.5 + 0.5 * math.sin(2.0 * math.pi * (0.8 * t + b * 0.15))
            bar_h = max(4, int(45 * energy * harmonic_mod + 4 * math.sin(t * 5 + b)))
            bx = eq_x + b * (bar_width + bar_gap)
            by = eq_y - bar_h
            # Color gradient: Cyan -> Emerald -> Purple
            col = (
                int(50 + 180 * (b / num_bars)),
                int(180 + 75 * (1.0 - b / num_bars)),
                int(230),
            )
            draw.rounded_rectangle([bx, by, bx + bar_width, eq_y], radius=3, fill=col)

        # 12. Lower Third Banner (Teacher Title & Subject)
        banner_x = 60
        banner_y = 600
        draw.rounded_rectangle([banner_x, banner_y, banner_x + 540, banner_y + 80], radius=10, fill=(20, 28, 44), outline=(60, 85, 130), width=2)
        # Glowing Live Dot
        draw.ellipse([banner_x + 20, banner_y + 22, banner_x + 36, banner_y + 38], fill=(50, 220, 120))
        # Text Callouts
        draw.text((banner_x + 48, banner_y + 14), teacher_name, fill=(255, 255, 255))
        draw.text((banner_x + 48, banner_y + 42), f"AI Teacher • {subject_title}", fill=(160, 190, 230))

        return img

    def generate_avatar_clip(
        self,
        audio_path: Path,
        output_path: Path,
        persona: str = "professor_alex",
        subject_title: str = "AI Teacher Lecture",
        teacher_name: str = "Prof. Alexander Vance",
    ) -> Path:
        """
        Synthesizes an authentic talking avatar MP4 clip synchronized to the provided TTS audio.
        Uses 2.5D audio-driven viseme generator at 30fps with FFmpeg rawvideo pipe.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check for pluggable Wav2Lip backend if requested and model checkpoint present
        wav2lip_model = Path(settings.project_root) / "models" / "wav2lip" / "wav2lip_gan.pth"
        if settings.avatar_engine == "wav2lip" and wav2lip_model.exists():
            try:
                logger.info(f"Using pluggable Wav2Lip backend at {wav2lip_model}")
                return self._run_wav2lip(audio_path, output_path)
            except Exception as e:
                logger.warning(f"Wav2Lip backend failed ({e}), falling back to 2.5D Viseme engine.")

        # Primary High-Speed 2.5D Viseme Engine
        envelope = self.extract_audio_energy_envelope(audio_path, fps=self.fps)
        total_frames = len(envelope)

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgb24",
            "-r", str(self.fps),
            "-i", "-",
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-tune", "animation",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path),
        ]

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        for f in range(total_frames):
            energy = float(envelope[f])
            frame_img = self.render_avatar_frame(
                frame_idx=f,
                total_frames=total_frames,
                energy=energy,
                persona=persona,
                subject_title=subject_title,
                teacher_name=teacher_name,
            )
            proc.stdin.write(frame_img.tobytes())

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            err = proc.stderr.read().decode(errors="ignore")
            logger.error(f"FFmpeg avatar rendering failed with return code {proc.returncode}: {err}")
            raise RuntimeError(f"FFmpeg avatar rendering failed: {err}")

        return output_path

    def _run_wav2lip(self, audio_path: Path, output_path: Path) -> Path:
        """Pluggable hook to execute Wav2Lip neural inference when weights are installed."""
        face_img = self.avatar_dir / "teacher_portrait.png"
        if not face_img.exists():
            # Generate reference base face frame
            base_frame = self.render_avatar_frame(0, 30, 0.0)
            base_frame.save(str(face_img))

        cmd = [
            "python3", "inference_wav2lip.py",
            "--checkpoint_path", str(Path(settings.project_root) / "models/wav2lip/wav2lip_gan.pth"),
            "--face", str(face_img),
            "--audio", str(audio_path),
            "--outfile", str(output_path),
        ]
        subprocess.run(cmd, check=True)
        return output_path


avatar_service = AvatarService()
