import sys
import os
sys.path.insert(0, os.path.abspath("venv_test/lib/python3.11/site-packages"))

import asyncio
import time
import edge_tts
from gtts import gTTS

def test_edge_tts():
    """Test Edge TTS generation for English and Hindi and extract word boundaries."""
    import asyncio
    text_en = "Hello and welcome to your AI lesson. Today we will explore quantum computing and neural networks."
    text_hi = "नमस्ते और आपकी एआई कक्षा में स्वागत है। आज हम क्वांटम कंप्यूटिंग और न्यूरल नेटवर्क सीखेंगे।"

    # Helper to run async calls
    def run_async(coro):
        return asyncio.run(coro)

    # 1. Test English edge-tts
    t0 = time.time()
    comm_en = edge_tts.Communicate(text_en, voice="en-US-GuyNeural")
    run_async(comm_en.save("test_scripts/test_en_edge.mp3"))
    t1 = time.time()
    print(f"Edge-TTS English generated in {t1 - t0:.2f}s (voice: en-US-GuyNeural)")

    # 2. Test Hindi edge-tts
    t0 = time.time()
    comm_hi = edge_tts.Communicate(text_hi, voice="hi-IN-MadhurNeural")
    run_async(comm_hi.save("test_scripts/test_hi_edge.mp3"))
    t1 = time.time()
    print(f"Edge-TTS Hindi generated in {t1 - t0:.2f}s (voice: hi-IN-MadhurNeural)")

    # 3. Test Word Boundary Extraction for Slide Sync / Subtitles
    words_timing = []
    async def extract():
        comm_words = edge_tts.Communicate(text_en, voice="en-US-GuyNeural")
        async for chunk in comm_words.stream():
            if chunk["type"] == "WordBoundary":
                words_timing.append({
                    "offset": chunk["offset"],
                    "duration": chunk["duration"],
                    "text": chunk["text"]
                })
    run_async(extract())
    print(f"Extracted {len(words_timing)} word boundaries from edge-tts stream!")

def test_gtts():
    text_en = "Hello, this is gTTS fallback voice."
    text_hi = "नमस्ते, यह gTTS बैकअप आवाज़ है।"
    
    t0 = time.time()
    tts_en = gTTS(text=text_en, lang='en')
    tts_en.save("test_scripts/test_en_gtts.mp3")
    t1 = time.time()
    print(f"gTTS English generated in {t1 - t0:.2f}s")
    
    t0 = time.time()
    tts_hi = gTTS(text=text_hi, lang='hi')
    tts_hi.save("test_scripts/test_hi_gtts.mp3")
    t1 = time.time()
    print(f"gTTS Hindi generated in {t1 - t0:.2f}s")

if __name__ == "__main__":
    print("--- Testing Edge-TTS ---")
    asyncio.run(test_edge_tts())
    print("\n--- Testing gTTS ---")
    test_gtts()
