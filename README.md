# Photo Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vision%20API-yellow.svg)](https://cloud.google.com/vision)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AI-powered image analysis system using Google Cloud Vision API and OpenAI GPT-4 for intelligent image understanding and Q&A capabilities.

## Technologies

- Google Cloud Vision API
- OpenAI GPT-4
- Sentence Transformers
- Python 3.11
- Streamlit
- Flask

## Installation

```bash
git clone https://github.com/e1washere/photo-assistant.git
cd photo-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Demo

Try the live demo or run locally:

```bash
# Quick demo with sample image
python main.py --demo

# Streamlit interface
python run_streamlit.py
```

## Usage

### Streamlit Interface
```bash
python run_streamlit.py
```

### Command Line
```bash
python main.py --image path/to/image.jpg
python main.py --image path/to/image.jpg --question "What objects do you see?"
```

### Flask API
```bash
python main.py --web
```

## Project Structure

```
photo-assistant/
├── main.py                 # CLI and Flask entry point
├── run_streamlit.py        # Streamlit launcher
├── cloud/                  # AI service integrations
│   ├── vision_api.py      # Google Cloud Vision client
│   └── llm_api.py         # OpenAI GPT-4 client
├── faq/                   # FAQ system
│   └── faq_handler.py     # Semantic search and Q&A
├── ui/                    # Web interfaces
│   ├── app.py            # Flask application
│   └── streamlit_app.py  # Streamlit application
├── data/                  # Data files
│   └── faq.json          # FAQ database
├── static/                # Static assets
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## API Documentation

### Core Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | Main application interface | `curl http://localhost:5000/` |
| `/upload` | POST | Upload and analyze image | `curl -X POST -F "file=@image.jpg" http://localhost:5000/upload` |
| `/ask` | POST | Ask questions about images | `curl -X POST -H "Content-Type: application/json" -d '{"question": "What objects do you see?", "filename": "image.jpg"}' http://localhost:5000/ask` |
| `/faq` | GET | Retrieve FAQ data | `curl http://localhost:5000/faq` |
| `/faq/answer` | POST | Semantic FAQ search | `curl -X POST -H "Content-Type: application/json" -d '{"query": "How to upload?"}' http://localhost:5000/faq/answer` |

### Response Format

```json
{
  "success": true,
  "vision_description": "This image contains: nature, landscape, outdoor",
  "llm_description": "A beautiful natural landscape featuring outdoor scenery",
  "labels": ["nature", "landscape", "outdoor"],
  "tags": ["nature", "landscape", "outdoor", "scenery"]
}
```

## Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Image Analysis** | Object detection, OCR, scene classification | Google Cloud Vision API |
| **Natural Language Q&A** | Ask questions about images in plain English | OpenAI GPT-4 |
| **Semantic Search** | Find relevant FAQ answers using embeddings | Sentence Transformers |
| **Multiple Interfaces** | Streamlit UI, CLI, REST API | Flask + Streamlit |
| **Real-time Processing** | Instant analysis and response generation | Async processing |

## Limitations

- Requires internet connection for cloud services
- Maximum 16MB file size
- API rate limits apply
- Images processed by external services

## API Endpoints

### Core Endpoints

- `GET /` - Main application interface
- `POST /upload` - Upload and analyze an image
- `POST /ask` - Ask questions about uploaded images
- `GET /faq` - Retrieve FAQ data
- `POST /faq/search` - Search FAQ questions
- `GET /health` - Health check endpoint

### Example Usage

```bash
# Upload an image
curl -X POST -F "file=@image.jpg" http://localhost:5000/upload

# Ask a question about an uploaded image
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What objects do you see?", "filename": "uploaded_image.jpg"}' \
  http://localhost:5000/ask
```

## Project Structure

```
photo-assistant/
├── main.py                 # Flask application entry point
├── run_streamlit.py        # Streamlit application launcher
├── cloud/                  # Cloud API integrations
│   ├── vision_api.py      # Google Cloud Vision API client
│   └── llm_api.py         # OpenAI GPT API client
├── faq/                   # FAQ management
│   └── faq_handler.py     # FAQ operations and semantic search
├── ui/                    # Web interface
│   ├── app.py            # Flask application and routes
│   └── streamlit_app.py  # Streamlit application
├── data/                  # Data files
│   └── faq.json          # FAQ database
├── static/                # Static assets
│   ├── uploads/          # Uploaded images (auto-created)
│   └── sample.jpg        # Sample image
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Development

### Code Quality

- **Type Hints**: All functions include comprehensive type annotations
- **Documentation**: Detailed docstrings for all public functions
- **Error Handling**: Robust error handling with graceful fallbacks
- **Testing**: Mock responses for development without API keys

### Adding Features

1. **New API Endpoints**: Add routes in `ui/app.py`
2. **FAQ Management**: Extend `faq/faq_handler.py`
3. **Vision Analysis**: Enhance `cloud/vision_api.py`
4. **LLM Integration**: Modify `cloud/llm_api.py`

## Deployment

### Production Deployment

1. Set production environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY="secure-production-key"
```

2. Use Gunicorn for production:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

## Security Considerations

- API keys are stored as environment variables
- File upload validation and size limits
- Secure filename handling
- CORS configuration for production
- Input sanitization and validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper type hints and documentation
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please refer to the FAQ section in the application or create an issue in the repository. 