import streamlit as st
import json
from typing import Dict, Any, Optional


def render_results_tab():
    st.header("📝 Results & Processing")
    
    st.markdown("View and process OCR results from the OCR tab or upload your own files.")
    
    tab1, tab2 = st.tabs(["📄 Current Results", "📁 Upload Files"])
    
    with tab1:
        render_current_results()
    
    with tab2:
        render_file_upload()


def render_current_results():
    if not st.session_state.markdown_content:
        st.info("💡 No OCR results available. Process a document in the OCR tab first.")
        return
    
    st.success("✅ OCR results loaded from OCR tab")
    display_and_process_results()


def render_file_upload():
    st.subheader("Upload OCR Results")
    st.markdown("Upload either a `.json` file (raw OCR results) or `.md` file (markdown output)")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["json", "md"],
        help="Upload JSON or Markdown files from previous OCR processing"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.json'):
                load_json_file(uploaded_file)
            elif uploaded_file.name.endswith('.md'):
                load_markdown_file(uploaded_file)
                
            st.success(f"✅ Successfully loaded {uploaded_file.name}")
            display_and_process_results()
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")


def load_json_file(uploaded_file):
    content = uploaded_file.read().decode('utf-8')
    ocr_data = json.loads(content)
    
    if 'pages' in ocr_data:
        st.session_state.ocr_result = ocr_data
        st.session_state.markdown_content = generate_markdown_from_json(ocr_data)
    else:
        raise ValueError("Invalid JSON format - missing 'pages' structure")


def load_markdown_file(uploaded_file):
    content = uploaded_file.read().decode('utf-8')
    st.session_state.markdown_content = content
    st.session_state.ocr_result = parse_markdown_to_pages(content)


def generate_markdown_from_json(ocr_data: Dict[str, Any]) -> str:
    markdown_text = ""
    for page in ocr_data.get("pages", []):
        page_number = page.get("index", "unknown")
        markdown_content = page.get("markdown", "")
        
        markdown_text += f"## Page {page_number}\n\n"
        markdown_text += markdown_content
        markdown_text += "\n\n---\n\n"
    
    return markdown_text


def parse_markdown_to_pages(markdown_content: str) -> Optional[Dict[str, Any]]:
    try:
        pages = []
        sections = markdown_content.split("## Page ")
        
        for i, section in enumerate(sections):
            if i == 0 and not section.strip().startswith("Page"):
                continue
                
            lines = section.split('\n')
            if lines:
                try:
                    page_number = int(lines[0].split()[0]) if lines[0].split() else i-1
                except:
                    page_number = i-1
                
                page_content = '\n'.join(lines[1:]).replace("---", "").strip()
                
                pages.append({
                    "index": page_number,
                    "markdown": page_content
                })
        
        return {"pages": pages} if pages else None
    except:
        return None


def display_and_process_results():
    if st.session_state.ocr_result:
        page_count = len(st.session_state.ocr_result.get("pages", []))
        st.markdown(f"**Document loaded:** {page_count} pages")
    
    display_by_pages()
    
    # Automatically process for TTS
    if st.session_state.markdown_content:
        process_for_tts()
        
        st.markdown("---")
        st.success("✅ Text automatically processed and ready for TTS!")
        st.info("💡 Navigate to the **Text-to-Speech tab** to convert to audio.")


def display_by_pages():
    st.subheader("📄 Content by Pages")
    
    if st.session_state.ocr_result:
        pages = st.session_state.ocr_result.get("pages", [])
        
        if not pages:
            st.warning("No page data found")
            return
            
        for page in pages:
            page_number = page.get("index", "unknown")
            markdown_content = page.get("markdown", "")
            
            with st.expander(f"Page {page_number}", expanded=False):
                if markdown_content.strip():
                    st.markdown(markdown_content)
                else:
                    st.info("No content extracted from this page")
    else:
        st.markdown("**Full Document:**")
        with st.expander("View All Content", expanded=True):
            st.markdown(st.session_state.markdown_content)


def process_for_tts():
    if not st.session_state.markdown_content:
        return
    
    processed_text = st.session_state.markdown_content
    
    # Basic processing - remove page separators
    processed_text = processed_text.replace("---", "")
    processed_text = processed_text.replace("## Page", "Page")
    
    # Store processed text
    st.session_state.processed_text = processed_text.strip()
    
    # Show preview
    with st.expander("👀 Preview Processed Text", expanded=False):
        preview = processed_text[:500] + "..." if len(processed_text) > 500 else processed_text
        st.text(preview)