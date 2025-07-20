"""
LLM API Integration

Provides natural language processing capabilities using OpenAI's GPT models
for intelligent question answering and photo analysis interpretation.
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
import requests


class LLMAPI:
    """OpenAI GPT API client for natural language processing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM API client.
        
        Args:
            api_key: OpenAI API key. If None, reads from environment.
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4"  # Default to GPT-4 for better image analysis
        
        if not self.api_key:
            print("Warning: No OpenAI API key provided. Using mock responses.")
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: The user's question or prompt
            context: Additional context (e.g., image analysis results)
            
        Returns:
            Generated response from the LLM
        """
        try:
            if not self.api_key:
                return self._get_mock_response(prompt)
            
            # Prepare the message
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"You are a helpful photo assistant. Use this context to answer: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return self._get_mock_response(prompt)
    
    def analyze_photo_with_question(self, image_analysis: Dict[str, Any], question: str) -> str:
        """
        Analyze a photo and answer a specific question about it.
        
        Args:
            image_analysis: Results from vision API analysis
            question: User's question about the photo
            
        Returns:
            Intelligent answer based on image analysis
        """
        # Format the analysis results for the LLM
        context = self._format_analysis_for_llm(image_analysis)
        
        prompt = f"""
        Based on the following image analysis, please answer this question: {question}
        
        Image Analysis:
        {context}
        
        Please provide a clear, helpful answer based on the available information.
        """
        
        return self.generate_response(prompt, context)
    
    def _format_analysis_for_llm(self, analysis: Dict[str, Any]) -> str:
        """
        Format vision API analysis results for LLM consumption.
        
        Args:
            analysis: Raw analysis results from vision API
            
        Returns:
            Formatted string for LLM context
        """
        if not analysis or 'responses' not in analysis:
            return "No image analysis data available."
        
        response = analysis['responses'][0]
        formatted_parts = []
        
        # Labels
        labels = response.get('labelAnnotations', [])
        if labels:
            label_text = "Detected objects/concepts: " + ", ".join(
                [f"{label['description']} ({label['score']:.2f})" for label in labels[:5]]
            )
            formatted_parts.append(label_text)
        
        # Text
        text_annotations = response.get('textAnnotations', [])
        if text_annotations:
            text_content = "Text found: " + text_annotations[0].get('description', '')
            formatted_parts.append(text_content)
        
        # Objects
        objects = response.get('localizedObjectAnnotations', [])
        if objects:
            object_text = "Specific objects: " + ", ".join(
                [f"{obj['name']} ({obj['score']:.2f})" for obj in objects[:3]]
            )
            formatted_parts.append(object_text)
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific details detected."
    
    def _get_mock_response(self, prompt: str) -> str:
        """Return mock response for development/testing."""
        mock_responses = {
            "what is in this image": "This appears to be a natural landscape with trees and outdoor scenery.",
            "describe the photo": "The image shows a beautiful outdoor scene with natural elements.",
            "what colors are present": "Based on the analysis, this image likely contains natural greens and earth tones.",
            "is there text in the image": "The analysis detected some text content in the image.",
            "what objects can you see": "I can see trees and other natural objects in this landscape image."
        }
        
        prompt_lower = prompt.lower()
        for key, response in mock_responses.items():
            if key in prompt_lower:
                return response
        
        return "I can see this is an image with various elements. Could you ask a more specific question about what you'd like to know?"
    
    def generate_description_tags(self, text: str) -> Tuple[str, List[str]]:
        """
        Generate image description and tags using OpenAI GPT-4 API.
        
        Args:
            text: Input text describing the image or image analysis results
            
        Returns:
            Tuple containing (description, tags_list)
        """
        try:
            if not self.api_key:
                return self._get_mock_description_tags(text)
            
            # Prepare the prompt for description and tags generation
            prompt = f"""
            Based on the following image analysis text, generate:
            1. A detailed, natural language description of the image (2-3 sentences)
            2. A list of relevant tags/keywords (5-10 tags)
            
            Image Analysis Text: {text}
            
            Please format your response as:
            DESCRIPTION: [your detailed description here]
            TAGS: [tag1, tag2, tag3, tag4, tag5]
            """
            
            # Prepare the message
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert image analyst. Generate clear, accurate descriptions and relevant tags based on image analysis data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            
            # Parse the response to extract description and tags
            description, tags = self._parse_description_tags_response(response_text)
            
            return description, tags
            
        except Exception as e:
            print(f"Error generating description and tags: {e}")
            return self._get_mock_description_tags(text)
    
    def _parse_description_tags_response(self, response_text: str) -> Tuple[str, List[str]]:
        """
        Parse the LLM response to extract description and tags.
        
        Args:
            response_text: Raw response from the LLM
            
        Returns:
            Tuple containing (description, tags_list)
        """
        try:
            lines = response_text.strip().split('\n')
            description = ""
            tags = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('DESCRIPTION:'):
                    description = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('TAGS:'):
                    tags_text = line.replace('TAGS:', '').strip()
                    # Remove brackets and split by comma
                    tags_text = tags_text.strip('[]')
                    tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            # Fallback if parsing fails
            if not description:
                description = "A detailed description of the image based on analysis."
            if not tags:
                tags = ["image", "analysis", "content"]
            
            return description, tags
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            return "Image analysis completed successfully.", ["image", "analysis"]
    
    def _get_mock_description_tags(self, text: str) -> Tuple[str, List[str]]:
        """Return mock description and tags for development/testing."""
        # Generate mock description based on input text
        if "nature" in text.lower() or "landscape" in text.lower():
            description = "A beautiful natural landscape featuring outdoor scenery with trees and natural elements."
            tags = ["nature", "landscape", "outdoor", "trees", "scenery", "natural"]
        elif "text" in text.lower():
            description = "An image containing text content that has been analyzed and extracted."
            tags = ["text", "document", "ocr", "content", "reading"]
        elif "face" in text.lower() or "person" in text.lower():
            description = "A portrait or image featuring people with detected faces and human elements."
            tags = ["portrait", "people", "face", "human", "person"]
        else:
            description = "An analyzed image with various detected elements and content."
            tags = ["image", "analysis", "content", "detected", "elements"]
        
        return description, tags 