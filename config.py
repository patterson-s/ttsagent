import os
import streamlit as st
from typing import Dict, Optional


class APIKeyManager:
    def __init__(self):
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
    
    def set_manual_keys(self, mistral_key: Optional[str], openai_key: Optional[str]):
        if mistral_key:
            self.mistral_key = mistral_key
        if openai_key:
            self.openai_key = openai_key
    
    def has_mistral_key(self) -> bool:
        return bool(self.mistral_key and len(self.mistral_key.strip()) > 0)
    
    def has_openai_key(self) -> bool:
        return bool(self.openai_key and len(self.openai_key.strip()) > 0)
    
    def get_env_status(self) -> Dict[str, bool]:
        return {
            "mistral_env": bool(os.getenv("MISTRAL_API_KEY")),
            "openai_env": bool(os.getenv("OPENAI_API_KEY"))
        }
    
    def get_status(self) -> Dict[str, bool]:
        return {
            "mistral": self.has_mistral_key(),
            "openai": self.has_openai_key()
        }


def init_session_state():
    if 'api_manager' not in st.session_state:
        st.session_state.api_manager = APIKeyManager()
    
    if 'ocr_result' not in st.session_state:
        st.session_state.ocr_result = None
    
    if 'processed_text' not in st.session_state:
        st.session_state.processed_text = None
    
    if 'markdown_content' not in st.session_state:
        st.session_state.markdown_content = None


MAX_TTS_CHARS = 4000
AVAILABLE_VOICES = ["alloy", "nova", "shimmer", "fable", "echo", "onyx"]