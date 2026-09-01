import re
from pathlib import Path

ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")

# Whitelist domain-specific technical words, proper names, and libraries
WHITELIST = {
    "fastapi", "uvicorn", "pydantic", "ffmpeg", "wav2lip", "sadtalker", "latentsync",
    "gtts", "viseme", "visemes", "rag", "mcq", "mcqs", "docx", "pptx", "txt", "pdf",
    "pygments", "matplotlib", "bidi", "devanagari", "matras", "invariants", "asymptotic",
    "scaffolding", "scaffolded", "re", "explanations", "explanation", "pre", "requisite",
    "prerequisites", "prerequisite", "okapi", "bm25", "cosine", "reciprocal", "demuxer",
    "rgb", "rgba", "movflags", "faststart", "transcode", "hud", "h264", "aac", "mp4",
    "wav", "mp3", "websocket", "websockets", "json", "sqlite", "sqlite3", "milvus",
    "dto", "dtos", "spa", "vite", "nextjs", "react", "tailwindcss", "tailwind",
    "llm", "llms", "groq", "gemini", "llama", "mit", "e2e", "cli", "params", "param",
    "auth", "cors", "pid", "pids", "uri", "uris", "url", "urls", "api", "apis", "sdk",
    "rest", "http", "https", "guidelines", "roadmap", "masterclass", "hot", "reloading",
    "truetype", "dejavu", "noto", "lohit", "utf", "unicode", "html5", "screencasts",
    "screencast", "hackathon", "async", "synchronous", "asynchronous", "streamable",
    "ingestion", "synthesizer", "synthesizers", "prosody", "aspirates", "phoneme", "phonemes",
    "phonetic", "phonology", "discontinuity", "asymptote", "organelle", "organelles",
    "mitochondria", "atp", "algebraic", "quotient", "quotients", "epsilon", "delta",
    "bylaws", "rubric", "rubrics", "formative", "summative", "pedagogical", "pedagogy",
    "inorder", "preorder", "postorder", "avl", "traversal", "recommender", "remediations",
    "remediation", "unscripted", "uninterrupted", "decoupled", "subsystems", "subsystem",
    "scalability", "metadata", "resilience", "topologies", "topology", "unprocessed"
}

def check_file_spelling(filepath):
    content = filepath.read_text(encoding='utf-8')
    # Strip code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # Strip inline code
    content = re.sub(r'`.*?`', '', content)
    # Strip HTML tags
    content = re.sub(r'<.*?>', '', content)
    # Strip urls
    content = re.sub(r'https?://\S+', '', content)
    # Strip Hindi Devanagari text (range \u0900-\u097f)
    content = re.sub(r'[\u0900-\u097F]+', '', content)
    # Strip LaTeX math formulas ($...$ or $$...$$)
    content = re.sub(r'\$\$.*?\$\$', '', content, flags=re.DOTALL)
    content = re.sub(r'\$.*?\$', '', content)

    # Extract english words
    words = re.findall(r'\b[A-Za-z]{3,}\b', content)
    print(f"Checking {filepath.name}: {len(words)} words scanned.")

for p in ['README.md', 'docs/architecture.md', 'docs/api_specification.md', 'docs/setup_and_deployment.md', 'docs/user_guide.md', 'docs/multilingual_support.md']:
    check_file_spelling(ROOT / p)
