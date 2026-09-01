import subprocess
import os

def stitch_lesson_segments_concat_demuxer(segment_paths, output_stitched_video):
    """
    Concatenates video segments using FFmpeg concat demuxer.
    Fastest and lowest CPU usage, exact audio/video sync.
    """
    concat_txt = "concat_inputs.txt"
    with open(concat_txt, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg}'\n")
            
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        "-movflags", "+faststart",
        output_stitched_video
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Concat Demuxer Error:\n{res.stderr}")
        return False
    print(f"Stitched video generated via concat demuxer: {output_stitched_video}")
    return True

def stitch_lesson_segments_filter_complex(segment_paths, output_stitched_video):
    """
    Concatenates video segments using FFmpeg filter_complex.
    Ensures 100% timebase, sample rate, and resolution normalization across all inputs.
    """
    inputs = []
    filter_parts = []
    
    for i, seg in enumerate(segment_paths):
        inputs.extend(["-i", seg])
        filter_parts.append(f"[{i}:v:0]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v{i}];")
        filter_parts.append(f"[{i}:a:0]aformat=sample_rates=44100:channel_layouts=stereo[a{i}];")
        
    concat_filter = "".join([f"[v{i}][a{i}]" for i in range(len(segment_paths))])
    concat_filter += f"concat=n={len(segment_paths)}:v=1:a=1[outv][outa]"
    
    full_filter = "".join(filter_parts) + concat_filter
    
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_stitched_video
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Filter Complex Error:\n{res.stderr}")
        return False
    print(f"Stitched video generated via filter_complex: {output_stitched_video}")
    return True

if __name__ == "__main__":
    segments = [
        "avatar_intro.mp4",
        "math_slide_segment.mp4",
        "code_slide_segment.mp4",
        "avatar_outro.mp4"
    ]
    print("--- Testing Filter Complex Pipeline ---")
    stitch_lesson_segments_filter_complex(segments, "complete_hybrid_lesson.mp4")
    print("--- Testing Concat Demuxer Pipeline ---")
    stitch_lesson_segments_concat_demuxer(segments, "complete_hybrid_lesson_fast.mp4")
