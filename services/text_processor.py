import re
from typing import Optional


class TextProcessor:
    @staticmethod
    def clean_for_tts(text: str) -> str:
        if not text:
            return ""
        
        cleaned = text
        
        # Remove page separators
        cleaned = cleaned.replace("---", "")
        
        # Convert page headers to spoken form
        cleaned = re.sub(r"## Page (\d+)", r"Page \1.", cleaned)
        cleaned = re.sub(r"# (.+)", r"\1.", cleaned)
        
        # Clean up multiple whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        cleaned = re.sub(r' +', ' ', cleaned)
        
        # Remove footnote references like [^0], [^1]
        cleaned = re.sub(r'\[\^\d+\]', '', cleaned)
        
        # Clean up mathematical notation for better speech
        cleaned = cleaned.replace('$', '')
        
        return cleaned.strip()
    
    @staticmethod
    def get_word_count(text: str) -> int:
        if not text:
            return 0
        # Rough estimate: split by whitespace
        return len(text.split())
    
    @staticmethod
    def get_character_count(text: str) -> int:
        return len(text) if text else 0
    
    @staticmethod
    def preview_text(text: str, max_chars: int = 300) -> str:
        if not text:
            return ""
        
        if len(text) <= max_chars:
            return text
        
        # Try to cut at a sentence or word boundary
        preview = text[:max_chars]
        last_period = preview.rfind('.')
        last_space = preview.rfind(' ')
        
        if last_period > max_chars * 0.8:
            return preview[:last_period + 1] + "..."
        elif last_space > max_chars * 0.8:
            return preview[:last_space] + "..."
        else:
            return preview + "..."