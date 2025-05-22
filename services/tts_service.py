import re
import html
import tempfile
from pathlib import Path
from typing import Generator, BinaryIO
import markdown
from openai import OpenAI
from config import MAX_TTS_CHARS


class TTSService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                # Create client with minimal parameters to avoid conflicts
                self._client = OpenAI(
                    api_key=self.api_key,
                    timeout=60.0,  # Explicit timeout
                )
            except TypeError as e:
                if "proxies" in str(e):
                    # Fallback for version compatibility issues
                    try:
                        # Try with even more minimal initialization
                        import openai
                        self._client = openai.OpenAI(api_key=self.api_key)
                    except Exception as fallback_error:
                        raise Exception(f"OpenAI client initialization failed. Try: pip install openai --upgrade. Error: {str(e)}")
                else:
                    raise Exception(f"Failed to initialize OpenAI client: {str(e)}")
            except Exception as e:
                raise Exception(f"Failed to initialize OpenAI client: {str(e)}")
        return self._client
    
    def strip_markdown(self, md: str) -> str:
        html_text = markdown.markdown(md)
        plain = re.sub(r"<[^>]+>", " ", html_text)
        return html.unescape(plain)
    
    def chunk_text(self, text: str, size: int = MAX_TTS_CHARS) -> Generator[str, None, None]:
        start, n = 0, len(text)
        while start < n:
            end = min(start + size, n)
            if end < n and text[end] not in {" ", "\n"}:
                end = text.rfind(" ", start, end) or end
            yield text[start:end].strip()
            start = end
    
    def synthesize_to_file(self, text: str, model: str, voice: str, output_path: Path) -> None:
        for i, block in enumerate(self.chunk_text(text)):
            file_mode = "wb" if i == 0 else "ab"
            with self.client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=block,
                response_format="mp3",
            ) as resp, open(output_path, file_mode) as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)
    
    def get_audio_preview(self, text: str, max_chars: int = 200) -> str:
        plain_text = self.strip_markdown(text)
        if len(plain_text) <= max_chars:
            return plain_text
        return plain_text[:max_chars] + "..."
    
    def estimate_chunks(self, text: str) -> int:
        plain_text = self.strip_markdown(text)
        return len(list(self.chunk_text(plain_text)))
    
    def estimate_duration_minutes(self, text: str) -> float:
        # Simple estimation without requiring API client
        plain_text = self.strip_markdown(text)
        char_count = len(plain_text)
        words = char_count / 5
        return words / 200