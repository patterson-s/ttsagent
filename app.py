import streamlit as st
from config import init_session_state
from ui.setup_tab import render_setup_tab
from ui.ocr_tab import render_ocr_tab
from ui.results_tab import render_results_tab
from ui.tts_tab import render_tts_tab


def main():
    st.set_page_config(
        page_title="OCR & TTS Processor",
        page_icon="🔄",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("🔄 OCR & Text-to-Speech Processor")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔑 Setup", 
        "📄 OCR Processing", 
        "📝 Results & Processing", 
        "🎵 Text-to-Speech"
    ])
    
    with tab1:
        render_setup_tab()
    
    with tab2:
        render_ocr_tab()
    
    with tab3:
        render_results_tab()
    
    with tab4:
        render_tts_tab()


if __name__ == "__main__":
    main()