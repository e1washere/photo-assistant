#!/usr/bin/env python3
"""
Photo Assistant - Main Application Entry Point

A professional photo analysis and FAQ system that leverages cloud vision APIs
and LLM capabilities to provide intelligent photo insights and answers.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.app import create_app
from cloud.vision_api import VisionAPI
from cloud.llm_api import LLMAPI
from faq.faq_handler import FAQHandler


def analyze_image_workflow(image_path: str, question: Optional[str] = None):
    """
    Complete workflow for image analysis and question answering.
    
    Args:
        image_path: Path to the image file
        question: Optional question about the image
    """
    print("🚀 Photo Assistant - Image Analysis Workflow")
    print("=" * 50)
    
    try:
        # Initialize services
        print("📡 Initializing services...")
        vision_api = VisionAPI()
        llm_api = LLMAPI()
        faq_handler = FAQHandler()
        print("✅ Services initialized successfully")
        
        # Check if image exists
        if not Path(image_path).exists():
            print(f"❌ Error: Image file not found at {image_path}")
            return
        
        print(f"\n📸 Loading image: {image_path}")
        
        # Step 1: Analyze image with Vision API
        print("\n🔍 Step 1: Analyzing image with Vision API...")
        vision_description, labels = vision_api.analyze_image(image_path)
        
        print(f"📝 Vision Description: {vision_description}")
        print(f"🏷️  Detected Labels: {', '.join(labels) if labels else 'None'}")
        
        # Step 2: Generate enhanced description and tags with LLM
        print("\n🤖 Step 2: Generating enhanced description and tags with LLM...")
        llm_description, tags = llm_api.generate_description_tags(vision_description)
        
        print(f"📝 Enhanced Description: {llm_description}")
        print(f"🏷️  Generated Tags: {', '.join(tags) if tags else 'None'}")
        
        # Step 3: Answer question if provided
        if question:
            print(f"\n❓ Step 3: Answering question: '{question}'")
            
            # Try FAQ first
            print("🔍 Searching FAQ...")
            faq_answer = faq_handler.answer_question(question)
            print(f"📚 FAQ Answer: {faq_answer}")
            
            # Get similar questions
            similar_questions = faq_handler.get_similar_questions(question, top_k=2)
            if similar_questions:
                print("🔗 Similar FAQ Questions:")
                for qa in similar_questions:
                    print(f"  - {qa[0]} (Similarity: {qa[2]:.2f})")
            
            # Generate LLM answer based on image analysis
            print("🤖 Generating LLM answer based on image...")
            analysis_result = {
                'responses': [{
                    'labelAnnotations': [{'description': label} for label in labels],
                    'description': vision_description
                }]
            }
            llm_answer = llm_api.analyze_photo_with_question(analysis_result, question)
            print(f"🤖 LLM Answer: {llm_answer}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"📸 Image: {image_path}")
        print(f"📝 Vision Description: {vision_description}")
        print(f"📝 Enhanced Description: {llm_description}")
        print(f"🏷️  Labels: {len(labels)} detected")
        print(f"🏷️  Tags: {len(tags)} generated")
        
        if question:
            print(f"❓ Question: {question}")
            print(f"📚 FAQ Answer: {faq_answer}")
            print(f"🤖 LLM Answer: {llm_answer}")
        
        print("\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


def run_flask_app():
    """Run the Flask web application."""
    try:
        # Initialize core services
        vision_api = VisionAPI()
        llm_api = LLMAPI()
        faq_handler = FAQHandler()
        
        # Create and run Flask application
        app = create_app(vision_api, llm_api, faq_handler)
        
        # Run in development mode
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=os.environ.get('FLASK_ENV') == 'development'
        )
        
    except Exception as e:
        print(f"Error starting Photo Assistant: {e}")
        sys.exit(1)


def main():
    """Main entry point with command line interface."""
    parser = argparse.ArgumentParser(
        description="Photo Assistant - AI-Powered Image Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an image
  python main.py --image path/to/image.jpg
  
  # Analyze image and answer a question
  python main.py --image path/to/image.jpg --question "What objects do you see?"
  
  # Run Flask web application
  python main.py --web
  
  # Run with sample image
  python main.py --image static/sample.jpg --question "Describe this image"
        """
    )
    
    parser.add_argument(
        '--image', '-i',
        type=str,
        help='Path to the image file to analyze'
    )
    
    parser.add_argument(
        '--question', '-q',
        type=str,
        help='Question to ask about the image'
    )
    
    parser.add_argument(
        '--web', '-w',
        action='store_true',
        help='Run the Flask web application'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo with sample image and question'
    )
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.web:
        print("🌐 Starting Photo Assistant Flask Web Application...")
        run_flask_app()
    elif args.demo:
        print("🎬 Running Photo Assistant Demo...")
        sample_image = Path(__file__).parent / "static" / "sample.jpg"
        if sample_image.exists():
            analyze_image_workflow(
                str(sample_image),
                "What can you tell me about this image?"
            )
        else:
            print("❌ Demo image not found. Please provide an image with --image")
    elif args.image:
        analyze_image_workflow(args.image, args.question)
    else:
        # Default: show help
        parser.print_help()
        print("\n💡 Tip: Use --demo to run a quick demonstration")


if __name__ == "__main__":
    main() 