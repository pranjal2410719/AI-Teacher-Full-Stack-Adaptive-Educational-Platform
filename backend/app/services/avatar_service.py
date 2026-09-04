"""
Photorealistic AI Teacher Avatar Service with Audio-Driven Viseme Compositing.
Synthesizes speech-synchronized talking head video clips from photorealistic portraits
using high-speed Region-of-Interest (ROI) viseme compositing, natural 3-frame eye blinking,
dynamic audio RMS energy lip-sync, and ApniHelp branded presentation overlays.
Includes pluggable Wav2Lip CLI backend.
"""

import os
import math
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.config import settings

logger = logging.getLogger(__name__)


class AvatarService:
    """High-speed Photorealistic Audio-Reactive Viseme Avatar Generator & Wav2Lip Adapter."""

    def __init__(self, avatar_dir: Optional[Path] = None):
        self.avatar_dir = Path(avatar_dir) if avatar_dir else settings.avatar_dir
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = settings.ffmpeg_path
        self.ffprobe_path = settings.ffprobe_path
        self.width = 1280
        self.height = 720
        self.fps = 30
        self._portrait_cache: Dict[str, Image.Image] = {}

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
            envelope = np.clip(envelope / 2000.0, 0.0, 1.0)

        # Smooth envelope with exponential moving average (alpha=0.4)
        smoothed = np.zeros_like(envelope)
        curr = 0.0
        for i, val in enumerate(envelope):
            curr = 0.4 * val + 0.6 * curr
            smoothed[i] = curr

        return smoothed

    def _resolve_base_portrait(self, persona: str = "professor_alex") -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Resolves cached photorealistic AI teacher portrait and facial landmark coordinates.
        Supports Dr. Sarah Vance (female) and Prof. Alexander Vance (male).
        """
        p_str = str(persona).lower()
        is_male = any(k in p_str for k in ["alex", "male", "madhur", "man"])
        cache_key = "male" if is_male else "female"

        if cache_key not in self._portrait_cache:
            filename = "teacher_portrait_male.png" if is_male else "teacher_portrait.png"
            candidates = [
                self.avatar_dir / filename,
                settings.avatar_dir / filename,
                settings.project_root / "data" / "avatars" / filename,
                settings.project_root / ".agents" / "explorer_r3_video_avatar" / filename,
            ]
            portrait_path = next((p for p in candidates if p.exists()), None)
            if portrait_path:
                img = Image.open(portrait_path).convert("RGB")
                if img.size != (self.width, self.height):
                    img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            else:
                # High quality studio backdrop fallback
                img = Image.new("RGB", (self.width, self.height), (18, 24, 38))
                draw = ImageDraw.Draw(img)
                for y in range(0, self.height, 4):
                    ratio = y / float(self.height)
                    draw.line([(0, y), (self.width, y)], fill=(int(18 + 12 * ratio), int(24 + 18 * ratio), int(38 + 24 * ratio)), width=4)
            self._portrait_cache[cache_key] = img

        base_img = self._portrait_cache[cache_key]

        if is_male:
            geo = {
                "key": "male",
                "default_name": "Prof. Alexander Vance",
                "mx": 670,
                "my": 252,
                "lex": 620,
                "rex": 725,
                "ey": 185,
                "skin_tone": (135, 95, 75),
                "lip_tone": (130, 40, 50),
            }
        else:
            geo = {
                "key": "female",
                "default_name": "Dr. Sarah Vance",
                "mx": 690,
                "my": 248,
                "lex": 645,
                "rex": 770,
                "ey": 185,
                "skin_tone": (155, 110, 95),
                "lip_tone": (145, 50, 60),
            }

        return base_img, geo

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
        Renders a single 1280x720 RGB frame for the photorealistic AI teacher avatar
        with audio RMS-energy driven viseme mouth compositing, natural 3-frame eye blinking,
        subtle head bobbing, audio equalizer visualizer HUD, and ApniHelp lower-third branding.
        """
        t = frame_idx / float(self.fps)
        base_img, geo = self._resolve_base_portrait(persona)

        # Subtle sinusoidal head bobbing (micro-motion)
        bob_y = int(1.2 * math.sin(2.0 * math.pi * 0.5 * t))
        bob_x = int(0.6 * math.sin(2.0 * math.pi * 0.25 * t))

        img = base_img.copy()
        draw = ImageDraw.Draw(img)

        mx = geo["mx"] + bob_x
        my = geo["my"] + bob_y
        lex = geo["lex"] + bob_x
        rex = geo["rex"] + bob_x
        ey = geo["ey"] + bob_y

        # Natural 3-Frame Periodic Eye Blinking (once every ~3.2s)
        blink_period = 96
        is_blinking = (frame_idx % blink_period) < 3
        if is_blinking:
            lid_color = geo["skin_tone"]
            draw.arc([lex - 24, ey - 7, lex + 24, ey + 7], start=0, end=180, fill=lid_color, width=4)
            draw.arc([rex - 24, ey - 7, rex + 24, ey + 7], start=0, end=180, fill=lid_color, width=4)

        # Audio RMS-Energy Driven Phonetic Viseme Mouth Compositing
        # States: closed/smile_rest (< 0.12), slight_open (0.12-0.35), wide_open (0.35-0.65), round_o (0.65-0.82), wide_open_stressed (>= 0.82)
        if energy < 0.12:
            # Viseme 0: Closed / Resting Mouth / Gentle Smile from portrait
            pass
        elif energy < 0.35:
            # Viseme 1: Slightly Open (m/b/p transition and modest consonants)
            open_h = int(4 + 6 * ((energy - 0.12) / 0.23))
            draw.ellipse([mx - 15, my - open_h // 2, mx + 15, my + open_h // 2], fill=(55, 18, 22))
            draw.line([(mx - 10, my - open_h // 2 + 1), (mx + 10, my - open_h // 2 + 1)], fill=(240, 240, 245), width=2)
        elif energy < 0.65:
            # Viseme 2: Wide Open (conversational open vowels 'e', 'a', 'i')
            open_h = int(10 + 8 * ((energy - 0.35) / 0.30))
            draw.ellipse([mx - 20, my - open_h // 2, mx + 20, my + open_h // 2], fill=(45, 15, 20))
            # Upper teeth
            draw.rectangle([mx - 14, my - open_h // 2, mx + 14, my - open_h // 2 + 3], fill=(245, 245, 248))
            # Tongue
            draw.ellipse([mx - 10, my + open_h // 2 - 5, mx + 10, my + open_h // 2], fill=(190, 75, 85))
        elif energy < 0.82:
            # Viseme 3: Round 'O' / 'U' shape
            open_h = int(14 + 6 * ((energy - 0.65) / 0.17))
            draw.ellipse([mx - 12, my - open_h // 2, mx + 12, my + open_h // 2], fill=(30, 10, 15))
            draw.ellipse([mx - 14, my - open_h // 2 - 2, mx + 14, my + open_h // 2 + 2], outline=geo["lip_tone"], width=2)
        else:
            # Viseme 4: Wide Open Stressed (exclamations / stressed open syllables)
            open_h = int(18 + 8 * min(1.0, (energy - 0.82) / 0.18))
            draw.ellipse([mx - 24, my - open_h // 2, mx + 24, my + open_h // 2], fill=(40, 12, 18))
            # Upper teeth
            draw.rectangle([mx - 16, my - open_h // 2, mx + 16, my - open_h // 2 + 4], fill=(245, 245, 248))
            # Tongue
            draw.ellipse([mx - 12, my + open_h // 2 - 7, mx + 12, my + open_h // 2], fill=(200, 80, 90))

        # Studio HUD: Audio Equalizer Visualizer Bars
        eq_x = 980
        eq_y = 660
        num_bars = 16
        bar_width = 12
        bar_gap = 5
        draw.rounded_rectangle([eq_x - 20, eq_y - 60, eq_x + num_bars * (bar_width + bar_gap) + 15, eq_y + 20], radius=8, fill=(15, 23, 42), outline=(51, 65, 85), width=1)
        for b in range(num_bars):
            harmonic_mod = 0.5 + 0.5 * math.sin(2.0 * math.pi * (0.8 * t + b * 0.15))
            bar_h = max(4, int(45 * energy * harmonic_mod + 4 * math.sin(t * 5 + b)))
            bx = eq_x + b * (bar_width + bar_gap)
            by = eq_y - bar_h
            col = (
                int(50 + 180 * (b / num_bars)),
                int(180 + 75 * (1.0 - b / num_bars)),
                int(230),
            )
            draw.rounded_rectangle([bx, by, bx + bar_width, eq_y], radius=3, fill=col)

        # Lower Third Presentation Banner (ApniHelp Theme)
        banner_x = 60
        banner_y = 600
        draw.rounded_rectangle([banner_x, banner_y, banner_x + 540, banner_y + 80], radius=10, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        # Amber/Yellow glowing live indicator
        draw.ellipse([banner_x + 20, banner_y + 22, banner_x + 36, banner_y + 38], fill=(234, 179, 8))
        # Text Callouts
        disp_name = teacher_name if teacher_name and teacher_name != "Prof. Alexander Vance" else geo["default_name"]
        draw.text((banner_x + 48, banner_y + 14), disp_name, fill=(255, 255, 255))
        draw.text((banner_x + 48, banner_y + 42), f"ApniHelp • {subject_title}", fill=(203, 213, 225))

        # Watermark Badge (ApniHelp Branding)
        draw.rounded_rectangle([self.width - 165, 18, self.width - 30, 52], radius=6, fill=(15, 23, 42))
        draw.text((self.width - 145, 26), "ApniHelp", fill=(100, 210, 170))

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
        Uses photorealistic ROI viseme compositing at 30fps with FFmpeg rawvideo pipe.
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
                logger.warning(f"Wav2Lip backend failed ({e}), falling back to Photorealistic Viseme engine.")

        # Primary High-Speed Photorealistic Viseme Engine
        envelope = self.extract_audio_energy_envelope(audio_path, fps=self.fps)
        total_frames = len(envelope)

        # Standardized encoding matching slide videos: 1280x720, 30fps, yuv420p, aac 44.1kHz stereo
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
            "-r", str(self.fps),
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-crf", "26",
            "-threads", "2",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
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

        base_img, geo = self._resolve_base_portrait(persona)
        # Pre-render static base frame with ApniHelp lower-third & watermark
        static_canvas = base_img.copy()
        draw_static = ImageDraw.Draw(static_canvas)
        banner_x = 60
        banner_y = 600
        draw_static.rounded_rectangle([banner_x, banner_y, banner_x + 540, banner_y + 80], radius=10, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        draw_static.ellipse([banner_x + 20, banner_y + 22, banner_x + 36, banner_y + 38], fill=(234, 179, 8))
        disp_name = teacher_name if teacher_name and teacher_name != "Prof. Alexander Vance" else geo["default_name"]
        draw_static.text((banner_x + 48, banner_y + 14), disp_name, fill=(255, 255, 255))
        draw_static.text((banner_x + 48, banner_y + 42), f"ApniHelp • {subject_title}", fill=(203, 213, 225))
        draw_static.rounded_rectangle([self.width - 165, 18, self.width - 30, 52], radius=6, fill=(15, 23, 42))
        draw_static.text((self.width - 145, 26), "ApniHelp", fill=(100, 210, 170))

        # Rest crops for high-speed ROI refreshing
        mx, my = geo["mx"], geo["my"]
        lex, rex, ey = geo["lex"], geo["rex"], geo["ey"]
        mouth_rest = static_canvas.crop((mx - 32, my - 16, mx + 32, my + 16))
        eye_l_rest = static_canvas.crop((lex - 26, ey - 10, lex + 26, ey + 10))
        eye_r_rest = static_canvas.crop((rex - 26, ey - 10, rex + 26, ey + 10))

        # Equalizer background box
        eq_x, eq_y = 980, 660
        num_bars = 16
        bar_width, bar_gap = 12, 5
        draw_static.rounded_rectangle([eq_x - 20, eq_y - 60, eq_x + num_bars * (bar_width + bar_gap) + 15, eq_y + 20], radius=8, fill=(15, 23, 42), outline=(51, 65, 85), width=1)
        hud_box_rest = static_canvas.crop((eq_x - 20, eq_y - 60, eq_x + num_bars * (bar_width + bar_gap) + 15, eq_y + 20))

        canvas = static_canvas.copy()
        draw_dyn = ImageDraw.Draw(canvas)

        for f in range(total_frames):
            energy = float(envelope[f])
            t = f / float(self.fps)

            # Restore base crops
            canvas.paste(mouth_rest, (mx - 32, my - 16))
            if (f % 96) == 3:  # Blink just ended
                canvas.paste(eye_l_rest, (lex - 26, ey - 10))
                canvas.paste(eye_r_rest, (rex - 26, ey - 10))

            # Dynamic viseme compositing
            if energy < 0.12:
                pass
            elif energy < 0.35:
                open_h = int(4 + 6 * ((energy - 0.12) / 0.23))
                draw_dyn.ellipse([mx - 15, my - open_h // 2, mx + 15, my + open_h // 2], fill=(55, 18, 22))
                draw_dyn.line([(mx - 10, my - open_h // 2 + 1), (mx + 10, my - open_h // 2 + 1)], fill=(240, 240, 245), width=2)
            elif energy < 0.65:
                open_h = int(10 + 8 * ((energy - 0.35) / 0.30))
                draw_dyn.ellipse([mx - 20, my - open_h // 2, mx + 20, my + open_h // 2], fill=(45, 15, 20))
                draw_dyn.rectangle([mx - 14, my - open_h // 2, mx + 14, my - open_h // 2 + 3], fill=(245, 245, 248))
                draw_dyn.ellipse([mx - 10, my + open_h // 2 - 5, mx + 10, my + open_h // 2], fill=(190, 75, 85))
            elif energy < 0.82:
                open_h = int(14 + 6 * ((energy - 0.65) / 0.17))
                draw_dyn.ellipse([mx - 12, my - open_h // 2, mx + 12, my + open_h // 2], fill=(30, 10, 15))
                draw_dyn.ellipse([mx - 14, my - open_h // 2 - 2, mx + 14, my + open_h // 2 + 2], outline=geo["lip_tone"], width=2)
            else:
                open_h = int(18 + 8 * min(1.0, (energy - 0.82) / 0.18))
                draw_dyn.ellipse([mx - 24, my - open_h // 2, mx + 24, my + open_h // 2], fill=(40, 12, 18))
                draw_dyn.rectangle([mx - 16, my - open_h // 2, mx + 16, my - open_h // 2 + 4], fill=(245, 245, 248))
                draw_dyn.ellipse([mx - 12, my + open_h // 2 - 7, mx + 12, my + open_h // 2], fill=(200, 80, 90))

            # Dynamic 3-frame eye blinking
            if (f % 96) < 3:
                lid_color = geo["skin_tone"]
                draw_dyn.arc([lex - 24, ey - 7, lex + 24, ey + 7], start=0, end=180, fill=lid_color, width=4)
                draw_dyn.arc([rex - 24, ey - 7, rex + 24, ey + 7], start=0, end=180, fill=lid_color, width=4)

            # Equalizer bars
            canvas.paste(hud_box_rest, (eq_x - 20, eq_y - 60))
            for b in range(num_bars):
                harmonic_mod = 0.5 + 0.5 * math.sin(2.0 * math.pi * (0.8 * t + b * 0.15))
                bar_h = max(4, int(45 * energy * harmonic_mod + 4 * math.sin(t * 5 + b)))
                bx = eq_x + b * (bar_width + bar_gap)
                by = eq_y - bar_h
                col = (
                    int(50 + 180 * (b / num_bars)),
                    int(180 + 75 * (1.0 - b / num_bars)),
                    int(230),
                )
                draw_dyn.rectangle([bx, by, bx + bar_width, eq_y], fill=col)

            proc.stdin.write(canvas.tobytes())

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
