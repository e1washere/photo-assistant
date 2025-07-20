import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from cloud.vision_api import VisionAPI


class TestVisionAPI:
    """Test cases for Vision API functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.vision_api = VisionAPI()
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        vision_api = VisionAPI()
        assert vision_api.api_key is None
        assert vision_api.client is None
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        api_key = "test-api-key"
        vision_api = VisionAPI(api_key=api_key)
        assert vision_api.api_key == api_key
    
    @patch('os.environ.get')
    def test_init_with_env_api_key(self, mock_env_get):
        """Test initialization with environment API key."""
        mock_env_get.return_value = "env-api-key"
        vision_api = VisionAPI()
        assert vision_api.api_key == "env-api-key"
    
    def test_analyze_image_file_not_found(self):
        """Test image analysis with non-existent file."""
        description, labels = self.vision_api.analyze_image("non_existent.jpg")
        assert "Error analyzing image" in description
        assert labels == []
    
    def test_analyze_image_with_mock_response(self):
        """Test image analysis with mock response."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_file_path = tmp_file.name
        
        try:
            description, labels = self.vision_api.analyze_image(tmp_file_path)
            assert "nature" in description.lower() or "landscape" in description.lower()
            assert len(labels) > 0
        finally:
            os.unlink(tmp_file_path)
    
    def test_generate_description_with_valid_data(self):
        """Test description generation with valid analysis data."""
        mock_analysis = {
            "responses": [{
                "labelAnnotations": [
                    {"description": "nature", "score": 0.95},
                    {"description": "landscape", "score": 0.89}
                ],
                "textAnnotations": [
                    {"description": "Sample text"}
                ],
                "localizedObjectAnnotations": [
                    {"name": "Tree", "score": 0.92}
                ]
            }]
        }
        
        description = self.vision_api._generate_description(mock_analysis)
        assert "nature" in description.lower()
        assert "landscape" in description.lower()
        assert "tree" in description.lower()
        assert "sample text" in description.lower()
    
    def test_generate_description_with_empty_data(self):
        """Test description generation with empty analysis data."""
        description = self.vision_api._generate_description({})
        assert "Unable to analyze image" in description
    
    def test_extract_labels_with_valid_data(self):
        """Test label extraction with valid data."""
        mock_analysis = {
            "responses": [{
                "labelAnnotations": [
                    {"description": "nature", "score": 0.95},
                    {"description": "landscape", "score": 0.89}
                ]
            }]
        }
        
        labels = self.vision_api._extract_labels(mock_analysis)
        assert labels == ["nature", "landscape"]
    
    def test_extract_labels_with_empty_data(self):
        """Test label extraction with empty data."""
        labels = self.vision_api._extract_labels({})
        assert labels == []
    
    def test_mock_response_structure(self):
        """Test that mock response has correct structure."""
        mock_response = self.vision_api._get_mock_response()
        
        assert "responses" in mock_response
        assert len(mock_response["responses"]) == 1
        assert "labelAnnotations" in mock_response["responses"][0]
        assert "textAnnotations" in mock_response["responses"][0]
        assert "localizedObjectAnnotations" in mock_response["responses"][0]
    
    @patch('requests.post')
    def test_api_request_with_key(self, mock_post):
        """Test API request when API key is provided."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "responses": [{
                "labelAnnotations": [
                    {"description": "test", "score": 0.9}
                ]
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        vision_api = VisionAPI(api_key="test-key")
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_file_path = tmp_file.name
        
        try:
            description, labels = vision_api.analyze_image(tmp_file_path)
            assert "test" in description.lower()
            assert labels == ["test"]
        finally:
            os.unlink(tmp_file_path)
    
    def test_extract_text_functionality(self):
        """Test text extraction functionality."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_file_path = tmp_file.name
        
        try:
            # This should work with mock responses
            texts = self.vision_api.extract_text(tmp_file_path)
            assert isinstance(texts, list)
        finally:
            os.unlink(tmp_file_path) 