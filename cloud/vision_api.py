"""
Cloud Vision API Integration

Provides image analysis capabilities using Google Cloud Vision API
for object detection, text recognition, and image classification.
"""

import os
import base64
from typing import Dict, List, Optional, Any, Tuple
import requests


class VisionAPI:
    """Google Cloud Vision API client for image analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vision API client.
        
        Args:
            api_key: Google Cloud Vision API key. If None, reads from environment.
        """
        self.api_key = api_key or os.environ.get('GOOGLE_CLOUD_VISION_API_KEY')
        self.base_url = "https://vision.googleapis.com/v1/images:annotate"
        
        if not self.api_key:
            print("Warning: No Google Cloud Vision API key provided. Using mock responses.")
    
    def analyze_image(self, image_path: str) -> Tuple[str, List[str]]:
        """
        Analyze an image using Google Cloud Vision API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple containing (description, labels_list)
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_content = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare request payload
            request_data = {
                "requests": [
                    {
                        "image": {
                            "content": image_content
                        },
                        "features": [
                            {"type": "LABEL_DETECTION"},
                            {"type": "TEXT_DETECTION"},
                            {"type": "OBJECT_LOCALIZATION"},
                            {"type": "FACE_DETECTION"}
                        ]
                    }
                ]
            }
            
            # Make API request
            if self.api_key:
                response = requests.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=request_data,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
            else:
                result = self._get_mock_response()
            
            # Extract description and labels
            description = self._generate_description(result)
            labels = self._extract_labels(result)
            
            return description, labels
                
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return "Error analyzing image", []
    
    def _generate_description(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate a natural language description from analysis results.
        
        Args:
            analysis_result: Raw analysis results from Vision API
            
        Returns:
            Natural language description of the image
        """
        if not analysis_result or 'responses' not in analysis_result:
            return "Unable to analyze image"
        
        response = analysis_result['responses'][0]
        description_parts = []
        
        # Labels
        labels = response.get('labelAnnotations', [])
        if labels:
            top_labels = [label['description'] for label in labels[:3]]
            description_parts.append(f"This image contains: {', '.join(top_labels)}")
        
        # Objects
        objects = response.get('localizedObjectAnnotations', [])
        if objects:
            object_names = [obj['name'] for obj in objects[:3]]
            description_parts.append(f"Objects detected: {', '.join(object_names)}")
        
        # Text
        text_annotations = response.get('textAnnotations', [])
        if text_annotations:
            text_content = text_annotations[0].get('description', '')
            if len(text_content) > 100:
                text_content = text_content[:100] + "..."
            description_parts.append(f"Text found: {text_content}")
        
        # Faces
        faces = response.get('faceAnnotations', [])
        if faces:
            description_parts.append(f"Contains {len(faces)} face(s)")
        
        if description_parts:
            return ". ".join(description_parts)
        else:
            return "No specific details detected in the image"
    
    def _extract_labels(self, analysis_result: Dict[str, Any]) -> List[str]:
        """
        Extract labels from analysis results.
        
        Args:
            analysis_result: Raw analysis results from Vision API
            
        Returns:
            List of label strings
        """
        if not analysis_result or 'responses' not in analysis_result:
            return []
        
        response = analysis_result['responses'][0]
        labels = response.get('labelAnnotations', [])
        
        return [label['description'] for label in labels]
    
    def _get_mock_response(self) -> Dict[str, Any]:
        """Return mock response for development/testing."""
        return {
            "responses": [
                {
                    "labelAnnotations": [
                        {"description": "nature", "score": 0.95},
                        {"description": "landscape", "score": 0.89},
                        {"description": "outdoor", "score": 0.87}
                    ],
                    "textAnnotations": [
                        {"description": "Sample text detected in image"}
                    ],
                    "localizedObjectAnnotations": [
                        {
                            "name": "Tree",
                            "score": 0.92,
                            "boundingPoly": {"normalizedVertices": []}
                        }
                    ]
                }
            ]
        }
    
    def extract_text(self, image_path: str) -> List[str]:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of extracted text strings
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_content = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare request payload for text detection only
            request_data = {
                "requests": [
                    {
                        "image": {
                            "content": image_content
                        },
                        "features": [
                            {"type": "TEXT_DETECTION"}
                        ]
                    }
                ]
            }
            
            # Make API request
            if self.api_key:
                response = requests.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=request_data,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
            else:
                result = self._get_mock_response()
            
            # Extract text
            text_annotations = result.get('responses', [{}])[0].get('textAnnotations', [])
            if text_annotations:
                return [annotation.get('description', '') for annotation in text_annotations[1:]]
            return []
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return []
    
    def get_labels(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Get image labels and their confidence scores.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of label dictionaries with description and score
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_content = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare request payload for label detection only
            request_data = {
                "requests": [
                    {
                        "image": {
                            "content": image_content
                        },
                        "features": [
                            {"type": "LABEL_DETECTION"}
                        ]
                    }
                ]
            }
            
            # Make API request
            if self.api_key:
                response = requests.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=request_data,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
            else:
                result = self._get_mock_response()
            
            return result.get('responses', [{}])[0].get('labelAnnotations', [])
            
        except Exception as e:
            print(f"Error getting labels: {e}")
            return [] 