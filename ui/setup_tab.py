import streamlit as st


def render_setup_tab():
    st.header("API Key Configuration")
    
    env_status = st.session_state.api_manager.get_env_status()
    
    if env_status["mistral_env"] or env_status["openai_env"]:
        st.success("🎉 Found API keys in environment variables!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mistral AI (OCR)")
        
        if env_status["mistral_env"]:
            st.success("✅ Found MISTRAL_API_KEY in environment")
        else:
            st.warning("⚠️ No MISTRAL_API_KEY in environment")
            
            mistral_key = st.text_input(
                "Enter Mistral API Key manually",
                type="password",
                help="Required for OCR functionality"
            )
            
            if mistral_key:
                st.session_state.api_manager.set_manual_keys(mistral_key, None)
                st.success("✅ Manual Mistral API key set")
    
    with col2:
        st.subheader("OpenAI (Text-to-Speech)")
        
        if env_status["openai_env"]:
            st.success("✅ Found OPENAI_API_KEY in environment")
        else:
            st.warning("⚠️ No OPENAI_API_KEY in environment")
            
            openai_key = st.text_input(
                "Enter OpenAI API Key manually",
                type="password",
                help="Required for Text-to-Speech functionality"
            )
            
            if openai_key:
                st.session_state.api_manager.set_manual_keys(None, openai_key)
                st.success("✅ Manual OpenAI API key set")
    
    st.markdown("---")
    
    status = st.session_state.api_manager.get_status()
    st.subheader("Service Availability")
    
    col1, col2 = st.columns(2)
    with col1:
        if status["mistral"]:
            st.success("📄 OCR Processing: Available")
        else:
            st.error("📄 OCR Processing: Not Available")
    
    with col2:
        if status["openai"]:
            st.success("🎵 Text-to-Speech: Available")
        else:
            st.error("🎵 Text-to-Speech: Not Available")
    
    if not any(status.values()):
        st.warning("💡 Set up at least one API key to use the app features")
    
    with st.expander("🔍 Environment Variable Setup", expanded=False):
        st.markdown("""
        **To set environment variables:**
        
        **Windows (Command Prompt):**
        ```
        set MISTRAL_API_KEY=your_key_here
        set OPENAI_API_KEY=your_key_here
        ```
        
        **Windows (PowerShell):**
        ```
        $env:MISTRAL_API_KEY="your_key_here"
        $env:OPENAI_API_KEY="your_key_here"
        ```
        
        **Linux/Mac:**
        ```
        export MISTRAL_API_KEY=your_key_here
        export OPENAI_API_KEY=your_key_here
        ```
        """)