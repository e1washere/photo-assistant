"""
Streamlit Photo Assistant Application

A modern web interface for the Photo Assistant using Streamlit,
providing image upload, analysis, and interactive Q&A capabilities.
"""

import streamlit as st
import sys
import os
from pathlib import Path
import tempfile
import uuid

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cloud.vision_api import VisionAPI
from cloud.llm_api import LLMAPI
from faq.faq_handler import FAQHandler


def initialize_services():
    """Initialize all service components."""
    try:
        vision_api = VisionAPI()
        llm_api = LLMAPI()
        faq_handler = FAQHandler()
        return vision_api, llm_api, faq_handler
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None


def analyze_image(vision_api, llm_api, image_file):
    """
    Analyze uploaded image using Vision API and LLM.
    
    Args:
        vision_api: Vision API instance
        llm_api: LLM API instance
        image_file: Uploaded file object
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(image_file.getvalue())
            tmp_path = tmp_file.name
        
        # Analyze with Vision API
        vision_description, labels = vision_api.analyze_image(tmp_path)
        
        # Generate enhanced description and tags with LLM
        llm_description, tags = llm_api.generate_description_tags(vision_description)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return {
            'vision_description': vision_description,
            'llm_description': llm_description,
            'labels': labels,
            'tags': tags,
            'success': True
        }
        
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        return {'success': False, 'error': str(e)}


def answer_question(llm_api, faq_handler, question, image_analysis=None):
    """
    Answer user question using LLM and FAQ system.
    
    Args:
        llm_api: LLM API instance
        faq_handler: FAQ handler instance
        question: User's question
        image_analysis: Optional image analysis results
        
    Returns:
        Dictionary with answer and related information
    """
    try:
        # First try FAQ system
        faq_answer = faq_handler.answer_question(question)
        similar_questions = faq_handler.get_similar_questions(question, top_k=3)
        
        # If we have image analysis, also get LLM answer
        llm_answer = None
        if image_analysis:
            # Create analysis result for LLM
            analysis_result = {
                'responses': [{
                    'labelAnnotations': [{'description': label} for label in image_analysis.get('labels', [])],
                    'description': image_analysis.get('vision_description', '')
                }]
            }
            llm_answer = llm_api.analyze_photo_with_question(analysis_result, question)
        
        return {
            'faq_answer': faq_answer,
            'llm_answer': llm_answer,
            'similar_questions': similar_questions,
            'success': True
        }
        
    except Exception as e:
        st.error(f"Error answering question: {e}")
        return {'success': False, 'error': str(e)}


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Photo Assistant - AI-Powered Image Analysis",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .tag {
        background-color: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    .label {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📸 Photo Assistant</h1>
        <p>AI-Powered Image Analysis & Intelligent Q&A</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize services
    vision_api, llm_api, faq_handler = initialize_services()
    
    if not all([vision_api, llm_api, faq_handler]):
        st.error("Failed to initialize services. Please check your configuration.")
        return
    
    # Sidebar for FAQ
    with st.sidebar:
        st.header("❓ FAQ Assistant")
        st.markdown("Ask general questions about the Photo Assistant:")
        
        faq_question = st.text_input("Your question:", key="faq_question")
        if st.button("Ask FAQ", key="faq_button"):
            if faq_question:
                with st.spinner("Searching FAQ..."):
                    faq_result = answer_question(llm_api, faq_handler, faq_question)
                
                if faq_result['success']:
                    st.success("**Answer:**")
                    st.write(faq_result['faq_answer'])
                    
                    if faq_result['similar_questions']:
                        st.markdown("**Similar Questions:**")
                        for qa in faq_result['similar_questions']:
                            with st.expander(f"{qa[0]} (Similarity: {qa[2]:.2f})"):
                                st.write(qa[1])
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 Upload & Analyze")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png', 'gif', 'webp'],
            help="Upload an image to analyze"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            # Analyze button
            if st.button("🔍 Analyze Image", type="primary"):
                with st.spinner("Analyzing image..."):
                    analysis_result = analyze_image(vision_api, llm_api, uploaded_file)
                
                if analysis_result['success']:
                    # Store results in session state
                    st.session_state['image_analysis'] = analysis_result
                    st.success("✅ Image analyzed successfully!")
                else:
                    st.error(f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}")
    
    with col2:
        st.header("💬 Ask Questions")
        
        # Question input
        question = st.text_input(
            "Ask a question about the image:",
            placeholder="e.g., What objects do you see? What colors are present?",
            key="question_input"
        )
        
        # Submit button
        if st.button("🤔 Ask Question", type="primary", key="ask_button"):
            if not question:
                st.warning("Please enter a question.")
            elif 'image_analysis' not in st.session_state:
                st.warning("Please upload and analyze an image first.")
            else:
                with st.spinner("Generating answer..."):
                    answer_result = answer_question(
                        llm_api, 
                        faq_handler, 
                        question, 
                        st.session_state['image_analysis']
                    )
                
                if answer_result['success']:
                    st.success("**Answer:**")
                    if answer_result['llm_answer']:
                        st.write(answer_result['llm_answer'])
                    else:
                        st.write(answer_result['faq_answer'])
                else:
                    st.error(f"❌ Error: {answer_result.get('error', 'Unknown error')}")
    
    # Results section
    if 'image_analysis' in st.session_state:
        st.header("📊 Analysis Results")
        
        analysis = st.session_state['image_analysis']
        
        # Create tabs for different result types
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Descriptions", "🏷️ Tags", "🏷️ Labels", "📋 Raw Data"])
        
        with tab1:
            st.subheader("Vision API Description")
            st.markdown(f"""
            <div class="result-box">
                {analysis['vision_description']}
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Enhanced LLM Description")
            st.markdown(f"""
            <div class="result-box">
                {analysis['llm_description']}
            </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Generated Tags")
            if analysis['tags']:
                tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in analysis['tags']])
                st.markdown(f"""
                <div class="result-box">
                    {tags_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No tags generated.")
        
        with tab3:
            st.subheader("Detected Labels")
            if analysis['labels']:
                labels_html = " ".join([f'<span class="label">{label}</span>' for label in analysis['labels']])
                st.markdown(f"""
                <div class="result-box">
                    {labels_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No labels detected.")
        
        with tab4:
            st.subheader("Raw Analysis Data")
            st.json(analysis)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Photo Assistant - Powered by Google Cloud Vision API & OpenAI GPT-4</p>
        <p>Built with Streamlit, Python, and AI/ML technologies</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main() 