"""
Configuration and Environment Settings for ApniHelp Core Platform.
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file from project root if present
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseModel):
    # App Information
    app_name: str = "ApniHelp Core Platform"
    app_version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"))
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    # Base Paths
    project_root: Path = PROJECT_ROOT
    data_dir: Path = PROJECT_ROOT / "data"
    upload_dir: Path = PROJECT_ROOT / "data" / "uploads"
    vector_index_dir: Path = PROJECT_ROOT / "data" / "indices"
    sessions_dir: Path = PROJECT_ROOT / "data" / "sessions"
    profiles_dir: Path = PROJECT_ROOT / "data" / "profiles"
    plans_dir: Path = PROJECT_ROOT / "data" / "plans"
    audio_dir: Path = PROJECT_ROOT / "data" / "audio"
    video_dir: Path = PROJECT_ROOT / "data" / "videos"
    avatar_dir: Path = PROJECT_ROOT / "data" / "avatars"
    slides_dir: Path = PROJECT_ROOT / "data" / "slides"

    # TTS & Video Generation Settings
    ffmpeg_path: str = Field(default_factory=lambda: os.getenv("FFMPEG_PATH", "ffmpeg"))
    ffprobe_path: str = Field(default_factory=lambda: os.getenv("FFPROBE_PATH", "ffprobe"))
    tts_default_voice_en: str = Field(default_factory=lambda: os.getenv("TTS_VOICE_EN", "en-US-GuyNeural"))
    tts_default_voice_hi: str = Field(default_factory=lambda: os.getenv("TTS_VOICE_HI", "hi-IN-MadhurNeural"))
    avatar_engine: str = Field(default_factory=lambda: os.getenv("AVATAR_ENGINE", "viseme_2_5d"))  # viseme_2_5d | wav2lip

    # LLM Settings (Free Tier Only)
    groq_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    groq_model: str = Field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    groq_fallback_model: str = Field(default_factory=lambda: os.getenv("GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant"))
    
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
    gemini_fallback_model: str = Field(default_factory=lambda: os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash"))
    
    embedding_model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-004"))
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "auto"))  # auto | groq | gemini | mock

    # Document Ingestion & Chunking
    max_upload_size_mb: int = Field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")))
    default_chunk_size: int = Field(default_factory=lambda: int(os.getenv("DEFAULT_CHUNK_SIZE", "500")))
    default_chunk_overlap: int = Field(default_factory=lambda: int(os.getenv("DEFAULT_CHUNK_OVERLAP", "100")))
    vector_dim: int = Field(default_factory=lambda: int(os.getenv("VECTOR_DIM", "768")))

    # Retrieval
    rag_top_k: int = Field(default_factory=lambda: int(os.getenv("RAG_TOP_K", "4")))
    hybrid_alpha: float = Field(default_factory=lambda: float(os.getenv("HYBRID_ALPHA", "0.6")))  # weight for vector vs BM25

    def init_directories(self) -> None:
        """Ensure all required runtime storage directories exist."""
        for directory in [
            self.data_dir,
            self.upload_dir,
            self.vector_index_dir,
            self.sessions_dir,
            self.profiles_dir,
            self.plans_dir,
            self.audio_dir,
            self.video_dir,
            self.avatar_dir,
            self.slides_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance and initialize storage directories."""
    settings = Settings()
    settings.init_directories()
    return settings


settings = get_settings()
