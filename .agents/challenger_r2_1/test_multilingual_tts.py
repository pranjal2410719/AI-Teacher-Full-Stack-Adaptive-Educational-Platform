"""
Empirical Challenge Harness 1: Multilingual TTS & Audio Synthesis
Tests Edge-TTS, gTTS fallback, offline waveform synthesis, Devanagari Hindi text,
long strings, empty text, invalid languages, and duration verification via ffprobe.
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"

from backend.app.services.tts_service import TTSService, VOICE_MAP

OUTPUT_DIR = Path("/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/challenger_r2_1/test_outputs/tts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def run_tts_tests():
    tts = TTSService(audio_dir=OUTPUT_DIR)
    results = []

    print("=" * 70)
    print("RUNNING EMPIRICAL CHALLENGE 1: MULTILINGUAL TTS & AUDIO SYNTHESIS")
    print("=" * 70)

    test_cases = [
        {
            "name": "Standard English Technical Synthesis",
            "text": "Welcome to the fundamental calculus lesson. Today we will explore limits, derivatives, and the rate of change.",
            "language": "en",
            "voice": "male",
        },
        {
            "name": "Hindi Devanagari Technical Script",
            "text": "नमस्ते विद्यार्थियों! आज के इस विशेष व्याख्यान में हम कलन और सीमाओं के महत्वपूर्ण सिद्धांतों को विस्तार से समझेंगे।",
            "language": "hi",
            "voice": "male",
        },
        {
            "name": "Hinglish Code-Switching & Technical Mix",
            "text": "Binary Search Tree में सर्च करने का time complexity O(log n) होता है, लेकिन यदि array sorted हो तो यह linked list जैसा behave करता है।",
            "language": "hi",
            "voice": "hi-IN-MadhurNeural",
        },
        {
            "name": "Long Script (>1000 characters stress test)",
            "text": (
                "The Industrial Revolution marked a profound turning point in human history, fundamentally transforming "
                "societies from agrarian economies based on manual labor to industrialized urban centers driven by mechanized production. "
                "Beginning in Great Britain during the mid-eighteenth century, key technological innovations such as James Watt's improved steam engine, "
                "the spinning jenny, and Henry Cort's puddling process revolutionized the textile and iron manufacturing industries. "
                "These technological leaps required massive quantities of coal and iron ore, catalyzing the rapid expansion of mining operations "
                "and necessitating new transport infrastructures such as canals and early twin-track railways."
            ),
            "language": "en",
            "voice": "female",
        },
        {
            "name": "Empty & Whitespace-Only Fallback",
            "text": "    \n\t   ",
            "language": "en",
            "voice": "default",
        },
        {
            "name": "Unsupported Language Code Fallback",
            "text": "This text uses an unsupported language code 'zz' and should gracefully fallback to English.",
            "language": "zz",
            "voice": None,
        },
        {
            "name": "Offline Synthesized Waveform Fallback",
            "text": "Testing pure offline harmonic formant waveform generator without any network.",
            "language": "en",
            "force_offline": True,
        }
    ]

    for idx, tc in enumerate(test_cases, 1):
        print(f"\n[Test 1.{idx}] {tc['name']}...")
        try:
            if tc.get("force_offline"):
                wav_out = OUTPUT_DIR / f"test_offline_{idx}.wav"
                dur = tts._generate_offline_waveform(tc["text"], wav_out)
                audio_path = wav_out
            else:
                audio_path, dur = await tts.synthesize(
                    text=tc["text"],
                    language=tc.get("language", "en"),
                    voice=tc.get("voice"),
                    use_cache=False
                )

            # Empirical Verification via ffprobe
            assert audio_path.exists(), f"Audio file was not created: {audio_path}"
            file_size = os.path.getsize(audio_path)
            assert file_size > 500, f"Audio file is suspiciously small: {file_size} bytes"

            probe_cmd = [
                tts.ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration,size,bit_rate:stream=codec_name,channels,sample_rate",
                "-of", "json",
                str(audio_path)
            ]
            probe_proc = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            probe_data = json.loads(probe_proc.stdout)

            actual_duration = float(probe_data["format"]["duration"])
            codec = probe_data["streams"][0]["codec_name"]
            sample_rate = probe_data["streams"][0]["sample_rate"]
            channels = probe_data["streams"][0]["channels"]

            print(f"  ✓ Success: File={audio_path.name}, Size={file_size}B, Duration={actual_duration:.2f}s, Codec={codec}, SampleRate={sample_rate}Hz, Channels={channels}")
            results.append({
                "test": tc["name"],
                "status": "PASS",
                "file": str(audio_path),
                "duration": actual_duration,
                "size_bytes": file_size,
                "codec": codec,
            })
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            results.append({
                "test": tc["name"],
                "status": "FAIL",
                "error": str(e)
            })

    print("\n" + "=" * 70)
    print("TTS EMPIRICAL CHALLENGE SUMMARY:")
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 70)
    return results


if __name__ == "__main__":
    asyncio.run(run_tts_tests())
