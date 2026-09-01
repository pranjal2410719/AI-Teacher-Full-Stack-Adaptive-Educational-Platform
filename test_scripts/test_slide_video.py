import subprocess
import os

def render_slide_video(image_file, audio_file, output_video):
    """
    Renders an animated/still visual slide segment synced exactly with TTS audio.
    Standardized to 1280x720 30fps yuv420p H.264 + AAC 44.1kHz.
    """
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_file,
        "-i", audio_file,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
        "-r", "30",
        "-shortest",
        "-movflags", "+faststart",
        output_video
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FFmpeg error:\n{res.stderr}")
        return False
    print(f"Successfully generated slide video: {output_video}")
    return True

if __name__ == "__main__":
    render_slide_video("math_slide.png", "test_en_edge.mp3", "math_slide_segment.mp4")
    render_slide_video("code_slide.png", "test_hi_edge.mp3", "code_slide_segment.mp4")
