import streamlit as st
import json
import time
from services.ocr_service import OCRService
from utils.file_helpers import save_uploaded_file, cleanup_temp_file, get_file_size_kb


def render_ocr_tab():
    st.header("📄 OCR Processing")
    
    if not st.session_state.api_manager.has_mistral_key():
        st.error("❌ Mistral API key required. Please configure it in the Setup tab.")
        return
    
    st.markdown("Upload a PDF document to extract text using Mistral AI's OCR capabilities.")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF document to extract text using OCR"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**File:** {uploaded_file.name}")
        with col2:
            file_size = get_file_size_kb(uploaded_file)
            st.info(f"**Size:** {file_size} KB")
        
        if st.button("🔍 Process Document", type="primary", use_container_width=True):
            process_document(uploaded_file)
    
    if st.session_state.ocr_result:
        display_ocr_results()


def process_document(uploaded_file):
    ocr_service = OCRService(st.session_state.api_manager.mistral_key)
    temp_file_path = None
    
    try:
        with st.status("Processing document...", expanded=True) as status:
            st.write("💾 Saving uploaded file...")
            temp_file_path = save_uploaded_file(uploaded_file)
            
            st.write("📤 Uploading to Mistral...")
            file_id = ocr_service.upload_pdf(temp_file_path)
            st.write(f"✅ File uploaded with ID: {file_id}")
            
            st.write("🔗 Getting signed URL...")
            signed_url = ocr_service.get_signed_url(file_id)
            st.write("✅ Got signed URL")
            
            st.write("🔍 Processing with OCR...")
            ocr_result = ocr_service.process_document(signed_url)
            st.write("✅ OCR processing complete")
            
            st.write("✨ Generating markdown...")
            markdown_content = ocr_service.generate_markdown_content(ocr_result)
            
            page_count = len(ocr_result.get("pages", []))
            st.write(f"📄 Processed {page_count} pages")
            
            st.session_state.ocr_result = ocr_result
            st.session_state.markdown_content = markdown_content
            
            time.sleep(0.5)
            status.update(label="✅ Processing complete!", state="complete")
            
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
    
    finally:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)


def display_ocr_results():
    st.markdown("---")
    st.subheader("📊 Processing Results")
    
    if st.session_state.ocr_result:
        page_count = len(st.session_state.ocr_result.get("pages", []))
        st.success(f"Successfully processed {page_count} pages")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📄 Download JSON",
                data=json.dumps(st.session_state.ocr_result, indent=2),
                file_name=f"ocr_result_{int(time.time())}.json",
                mime="application/json"
            )
        
        with col2:
            st.download_button(
                label="📝 Download Markdown",
                data=st.session_state.markdown_content,
                file_name=f"ocr_result_{int(time.time())}.md",
                mime="text/markdown"
            )
        
        with col3:
            if st.button("➡️ Send to Results Tab", type="secondary"):
                st.success("✅ Results sent to Results tab!")
                st.info("💡 Navigate to the Results & Processing tab to continue.")
        
        with st.expander("👀 Preview Results", expanded=False):
            st.markdown("**Extracted Text Preview:**")
            preview_text = st.session_state.markdown_content[:500] + "..." if len(st.session_state.markdown_content) > 500 else st.session_state.markdown_content
            st.text(preview_text)