import sys
import os

# Dynamically find workspace root and venv site-packages
script_dir = os.path.dirname(os.path.abspath(__file__))
ws_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "test_scripts" else script_dir
venv_site = os.path.join(ws_root, "venv_test", "lib", "python3.11", "site-packages")
if os.path.exists(venv_site):
    sys.path.insert(0, venv_site)

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import subprocess
import wave

def create_base_teacher_avatar(width=1280, height=720):
    """Generates a high-quality stylized avatar presentation frame."""
    canvas = Image.new("RGBA", (width, height), "#0F172A")
    draw = ImageDraw.Draw(canvas)
    
    # Background gradient / tech grid
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill="#1E293B", width=1)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill="#1E293B", width=1)
        
    # Center Spotlight Circle
    center_x, center_y = width // 2, height // 2 - 20
    draw.ellipse([(center_x - 220, center_y - 220), (center_x + 220, center_y + 220)], fill="#1E293B", outline="#38BDF8", width=4)
    
    # Teacher Avatar (Stylized Vector Character)
    # Head / Face
    face_bbox = (center_x - 110, center_y - 140, center_x + 110, center_y + 110)
    draw.ellipse(face_bbox, fill="#FCD34D", outline="#D97706", width=3) # Face skin
    
    # Hair
    draw.chord([(center_x - 115, center_y - 165), (center_x + 115, center_y - 30)], 180, 360, fill="#374151")
    
    # Glasses
    draw.rectangle([(center_x - 85, center_y - 45), (center_x - 15, center_y + 5)], outline="#1E293B", width=4, fill="#E0F2FE")
    draw.rectangle([(center_x + 15, center_y - 45), (center_x + 85, center_y + 5)], outline="#1E293B", width=4, fill="#E0F2FE")
    draw.line([(center_x - 15, center_y - 20), (center_x + 15, center_y - 20)], fill="#1E293B", width=4)
    
    # Eyes (open)
    draw.ellipse([(center_x - 55, center_y - 25), (center_x - 45, center_y - 15)], fill="#0F172A")
    draw.ellipse([(center_x + 45, center_y - 25), (center_x + 55, center_y - 15)], fill="#0F172A")
    
    # Eyebrows
    draw.line([(center_x - 75, center_y - 55), (center_x - 25, center_y - 50)], fill="#1F2937", width=4)
    draw.line([(center_x + 25, center_y - 50), (center_x + 75, center_y - 55)], fill="#1F2937", width=4)
    
    # Shoulders / Blazer
    draw.polygon([(center_x - 240, height), (center_x - 90, center_y + 100), (center_x + 90, center_y + 100), (center_x + 240, height)], fill="#1E3A8A")
    draw.polygon([(center_x - 70, center_y + 100), (center_x, center_y + 220), (center_x + 70, center_y + 100)], fill="#F8FAFC") # Shirt
    draw.polygon([(center_x - 20, center_y + 120), (center_x, center_y + 240), (center_x + 20, center_y + 120)], fill="#DC2626") # Tie
    
    # Teacher Name Card Badge
    draw.rectangle([(center_x - 180, height - 110), (center_x + 180, height - 40)], fill="#0B0F19", outline="#38BDF8", width=2)
    draw.text((center_x - 130, height - 98), "AI TEACHER: PROF. ALEX", fill="#38BDF8")
    draw.text((center_x - 150, height - 75), "Autonomous Multilingual Instructor", fill="#94A3B8")
    
    return canvas, (center_x, center_y)

def extract_audio_energy(audio_file, fps=30):
    """Extracts frame-by-frame speech energy/RMS from an audio file."""
    wav_path = "temp_avatar_audio.wav"
    subprocess.run(["ffmpeg", "-y", "-i", audio_file, "-ar", "16000", "-ac", "1", wav_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    with wave.open(wav_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_data = wf.readframes(n_frames)
        
    samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
    samples = samples / (np.max(np.abs(samples)) + 1e-6) # Normalize to [-1, 1]
    
    samples_per_video_frame = int(sample_rate / fps)
    total_video_frames = int(len(samples) / samples_per_video_frame)
    
    energy_per_frame = []
    for i in range(total_video_frames):
        chunk = samples[i * samples_per_video_frame : (i + 1) * samples_per_video_frame]
        rms = np.sqrt(np.mean(chunk**2))
        energy_per_frame.append(float(rms))
        
    return energy_per_frame, total_video_frames, wav_path

def generate_talking_avatar_video(audio_file, output_video="avatar_segment.mp4"):
    """Generates an audio-reactive talking avatar video segment."""
    base_canvas, (center_x, center_y) = create_base_teacher_avatar()
    fps = 30
    energy_frames, total_frames, wav_path = extract_audio_energy(audio_file, fps=fps)
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1280x720",
        "-pix_fmt", "rgba",
        "-r", str(fps),
        "-i", "-", # Stdin pipe
        "-i", audio_file,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        output_video
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for frame_idx, energy in enumerate(energy_frames):
        frame = base_canvas.copy()
        draw = ImageDraw.Draw(frame)
        
        # 1. Subtle head bobbing
        bob_offset = int(math.sin(frame_idx * 0.1) * 3)
        
        # 2. Eye blinking (every ~100 frames for 4 frames)
        is_blinking = (frame_idx % 110) in [0, 1, 2, 3]
        if is_blinking:
            draw.rectangle([(center_x - 60, center_y - 25 + bob_offset), (center_x - 40, center_y - 15 + bob_offset)], fill="#E0F2FE")
            draw.rectangle([(center_x + 40, center_y - 25 + bob_offset), (center_x + 60, center_y - 15 + bob_offset)], fill="#E0F2FE")
            draw.line([(center_x - 60, center_y - 20 + bob_offset), (center_x - 40, center_y - 20 + bob_offset)], fill="#1E293B", width=3)
            draw.line([(center_x + 40, center_y - 20 + bob_offset), (center_x + 60, center_y - 20 + bob_offset)], fill="#1E293B", width=3)
            
        # 3. Dynamic Mouth Visemes based on audio energy
        mouth_center_y = center_y + 45 + bob_offset
        
        # Clear mouth region with face skin tone
        draw.rectangle([(center_x - 45, mouth_center_y - 25), (center_x + 45, mouth_center_y + 35)], fill="#FCD34D")
        
        if energy < 0.04:
            draw.arc([(center_x - 25, mouth_center_y - 15), (center_x + 25, mouth_center_y + 10)], 0, 180, fill="#78350F", width=3)
        elif energy < 0.12:
            draw.ellipse([(center_x - 20, mouth_center_y - 8), (center_x + 20, mouth_center_y + 12)], fill="#881337", outline="#78350F", width=2)
            draw.rectangle([(center_x - 12, mouth_center_y - 6), (center_x + 12, mouth_center_y - 1)], fill="#FFFFFF")
        elif energy < 0.22:
            draw.ellipse([(center_x - 25, mouth_center_y - 12), (center_x + 25, mouth_center_y + 20)], fill="#881337", outline="#78350F", width=2)
            draw.rectangle([(center_x - 16, mouth_center_y - 10), (center_x + 16, mouth_center_y - 3)], fill="#FFFFFF")
            draw.ellipse([(center_x - 12, mouth_center_y + 8), (center_x + 12, mouth_center_y + 18)], fill="#F43F5E")
        else:
            draw.ellipse([(center_x - 30, mouth_center_y - 16), (center_x + 30, mouth_center_y + 28)], fill="#881337", outline="#78350F", width=2)
            draw.rectangle([(center_x - 20, mouth_center_y - 14), (center_x + 20, mouth_center_y - 6)], fill="#FFFFFF")
            draw.ellipse([(center_x - 15, mouth_center_y + 12), (center_x + 15, mouth_center_y + 25)], fill="#F43F5E")
            
        # 4. Audio Visualizer Equalizer Bar
        bar_x = 1000
        for b in range(10):
            bh = int(min(60, max(5, energy * 200 * (1 + 0.3 * math.sin(frame_idx + b)))))
            col = "#38BDF8" if b < 6 else ("#FBBF24" if b < 8 else "#F43F5E")
            draw.rectangle([(bar_x + b * 20, 680 - bh), (bar_x + b * 20 + 12, 680)], fill=col)
            
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print(f"Generated Talking Avatar Video at {output_video} ({total_frames} frames)")

if __name__ == "__main__":
    generate_talking_avatar_video("test_en_edge.mp3", "avatar_intro.mp4")
    generate_talking_avatar_video("test_hi_edge.mp3", "avatar_outro.mp4")
