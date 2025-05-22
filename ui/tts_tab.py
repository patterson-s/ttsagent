import streamlit as st
import tempfile
import time
from pathlib import Path
from services.tts_service import TTSService
from services.text_processor import TextProcessor
from config import AVAILABLE_VOICES


def render_tts_tab():
    st.header("🎵 Text-to-Speech")
    
    if not st.session_state.api_manager.has_openai_key():
        st.error("❌ OpenAI API key required. Please configure it in the Setup tab.")
        return
    
    tab1, tab2 = st.tabs(["🎤 Convert to Audio", "📄 Upload Text File"])
    
    with tab1:
        render_convert_from_results()
    
    with tab2:
        render_upload_text_file()


def render_convert_from_results():
    if not st.session_state.processed_text:
        st.info("💡 No processed text available. Process a document in the Results tab first.")
        return
    
    st.success("✅ Text loaded from Results tab")
    
    display_text_stats(st.session_state.processed_text)
    
    with st.expander("🔧 Text Processing Options", expanded=False):
        if st.button("🧹 Clean Text for TTS", key="clean_results_text"):
            clean_text_for_tts()
    
    render_tts_interface(st.session_state.processed_text)


def render_upload_text_file():
    st.subheader("Upload Text File")
    st.markdown("Upload a `.txt` or `.md` file to convert to speech")
    
    uploaded_file = st.file_uploader(
        "Choose a text file",
        type=["txt", "md"],
        help="Upload text or markdown files for TTS conversion",
        key="tts_file_upload"
    )
    
    if uploaded_file:
        try:
            content = uploaded_file.read().decode('utf-8')
            st.success(f"✅ Loaded {uploaded_file.name}")
            
            display_text_stats(content)
            
            with st.expander("🔧 Text Processing Options", expanded=True):
                if st.button("🧹 Clean Text for TTS", key="clean_upload_text"):
                    content = TextProcessor.clean_for_tts(content)
                    st.success("✅ Text cleaned for TTS")
                    
                with st.expander("👀 Preview Cleaned Text"):
                    preview = TextProcessor.preview_text(content, 400)
                    st.text(preview)
            
            render_tts_interface(content)
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")


def display_text_stats(text: str):
    if not text:
        return
    
    processor = TextProcessor()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        word_count = processor.get_word_count(text)
        st.metric("Words", f"{word_count:,}")
    
    with col2:
        char_count = processor.get_character_count(text)
        st.metric("Characters", f"{char_count:,}")
    
    with col3:
        try:
            if st.session_state.api_manager.has_openai_key():
                tts_service = TTSService(st.session_state.api_manager.openai_key)
                duration = tts_service.estimate_duration_minutes(text)
                st.metric("Est. Duration", f"{duration:.1f} min")
            else:
                st.metric("Est. Duration", "N/A")
        except Exception:
            st.metric("Est. Duration", "Error")


def clean_text_for_tts():
    if st.session_state.processed_text:
        cleaned = TextProcessor.clean_for_tts(st.session_state.processed_text)
        st.session_state.processed_text = cleaned
        st.success("✅ Text cleaned for TTS")


def render_tts_interface(text: str):
    if not text:
        st.warning("No text available for conversion")
        return
    
    st.markdown("---")
    st.subheader("🎵 Audio Conversion")
    
    col1, col2 = st.columns(2)
    
    with col1:
        voice = st.selectbox(
            "Select Voice",
            AVAILABLE_VOICES,
            help="Choose the voice for text-to-speech conversion"
        )
    
    with col2:
        model = st.radio(
            "Quality",
            ["Fast (tts-1)", "High-quality (tts-1-hd)"],
            horizontal=True,
            help="Higher quality takes longer but sounds better"
        )
        model_name = "tts-1-hd" if "hd" in model else "tts-1"
    
    # Preview section
    with st.expander("👀 Text Preview", expanded=False):
        preview = TextProcessor.preview_text(text, 500)
        st.text(preview)
    
    # Generate button
    if st.button("🎵 Generate Audio", type="primary", use_container_width=True):
        generate_audio(text, model_name, voice)


def generate_audio(text: str, model: str, voice: str):
    if not text.strip():
        st.error("No text to convert")
        return
    
    tts_service = TTSService(st.session_state.api_manager.openai_key)
    
    try:
        with st.status("Generating audio...", expanded=True) as status:
            st.write("🔄 Preparing text...")
            
            # Clean text
            clean_text = TextProcessor.clean_for_tts(text)
            chunk_count = tts_service.estimate_chunks(clean_text)
            
            st.write(f"📊 Processing {chunk_count} chunks...")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)
            
            st.write("🎵 Synthesizing audio...")
            tts_service.synthesize_to_file(clean_text, model, voice, tmp_path)
            
            st.write("✅ Audio generation complete!")
            status.update(label="✅ Audio ready!", state="complete")
            
            # Read and display audio
            audio_data = tmp_path.read_bytes()
            
            st.markdown("---")
            st.subheader("🎧 Generated Audio")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.audio(audio_data, format="audio/mp3")
            
            with col2:
                st.download_button(
                    label="📥 Download MP3",
                    data=audio_data,
                    file_name=f"tts_audio_{int(time.time())}.mp3",
                    mime="audio/mpeg"
                )
            
            # Cleanup
            tmp_path.unlink()
            
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")