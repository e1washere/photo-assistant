#!/usr/bin/env python3
"""
Comprehensive functionality test for Photo Assistant
Tests all components without requiring API keys
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from cloud.vision_api import VisionAPI
        print("✅ VisionAPI imported successfully")
    except Exception as e:
        print(f"❌ VisionAPI import failed: {e}")
        return False
    
    try:
        from cloud.llm_api import LLMAPI
        print("✅ LLMAPI imported successfully")
    except Exception as e:
        print(f"❌ LLMAPI import failed: {e}")
        return False
    
    try:
        from faq.faq_handler import FAQHandler
        print("✅ FAQHandler imported successfully")
    except Exception as e:
        print(f"❌ FAQHandler import failed: {e}")
        return False
    
    return True

def test_vision_api():
    """Test Vision API functionality"""
    print("\n🔍 Testing Vision API...")
    
    try:
        from cloud.vision_api import VisionAPI
        vision_api = VisionAPI()
        
        # Test with mock data
        description, labels = vision_api.analyze_image("test_image.jpg")
        
        print(f"✅ Vision API returned description: {description[:50]}...")
        print(f"✅ Vision API returned labels: {labels}")
        
        return True
    except Exception as e:
        print(f"❌ Vision API test failed: {e}")
        return False

def test_llm_api():
    """Test LLM API functionality"""
    print("\n🔍 Testing LLM API...")
    
    try:
        from cloud.llm_api import LLMAPI
        llm_api = LLMAPI()
        
        # Test with mock data
        description, tags = llm_api.generate_description_tags("A beautiful landscape with mountains")
        
        print(f"✅ LLM API returned description: {description[:50]}...")
        print(f"✅ LLM API returned tags: {tags}")
        
        return True
    except Exception as e:
        print(f"❌ LLM API test failed: {e}")
        return False

def test_faq_handler():
    """Test FAQ Handler functionality"""
    print("\n🔍 Testing FAQ Handler...")
    
    try:
        from faq.faq_handler import FAQHandler
        faq_handler = FAQHandler()
        
        # Test FAQ search
        answer = faq_handler.answer_question("How do I upload an image?")
        
        print(f"✅ FAQ Handler returned answer: {answer[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ FAQ Handler test failed: {e}")
        return False

def test_integration():
    """Test full integration workflow"""
    print("\n🔍 Testing full integration...")
    
    try:
        from cloud.vision_api import VisionAPI
        from cloud.llm_api import LLMAPI
        from faq.faq_handler import FAQHandler
        
        vision_api = VisionAPI()
        llm_api = LLMAPI()
        faq_handler = FAQHandler()
        
        # Simulate full workflow
        print("📸 Step 1: Analyzing image...")
        vision_desc, vision_labels = vision_api.analyze_image("test_image.jpg")
        
        print("🤖 Step 2: Generating enhanced description...")
        llm_desc, llm_tags = llm_api.generate_description_tags(vision_desc)
        
        print("❓ Step 3: Answering FAQ question...")
        faq_answer = faq_handler.answer_question("What can this system do?")
        
        print("✅ Full integration test completed successfully!")
        print(f"   Vision: {vision_desc[:30]}...")
        print(f"   LLM: {llm_desc[:30]}...")
        print(f"   FAQ: {faq_answer[:30]}...")
        
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_ui_components():
    """Test UI components can be imported"""
    print("\n🔍 Testing UI components...")
    
    try:
        # Test Flask app creation function
        from ui.app import create_app
        print("✅ Flask app creation function imported successfully")
        
        # Test Streamlit app
        import ui.streamlit_app
        print("✅ Streamlit app imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Photo Assistant Functionality Tests\n")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Vision API", test_vision_api),
        ("LLM API", test_llm_api),
        ("FAQ Handler", test_faq_handler),
        ("Integration", test_integration),
        ("UI Components", test_ui_components),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Photo Assistant is working correctly.")
        print("\n✅ What this means:")
        print("   - All components can be imported")
        print("   - Mock responses work without API keys")
        print("   - Integration workflow functions")
        print("   - UI components are ready")
        print("\n🚀 Next steps:")
        print("   - Add your API keys to test real functionality")
        print("   - Run 'python3 run_streamlit.py' for web interface")
        print("   - Run 'python3 main.py --demo' for CLI demo")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   - Ensure all dependencies are installed")
        print("   - Check Python version compatibility")
        print("   - Verify file paths and imports")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 