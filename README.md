# Photo Assistant - AI-Powered Image Analysis System

[![CI/CD](https://github.com/e1washere/photo-assistant/workflows/CI%2FCD/badge.svg)](https://github.com/e1washere/photo-assistant/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/e1washere/photo-assistant/actions)

A comprehensive photo analysis and FAQ system that leverages cloud vision APIs and LLM capabilities to provide intelligent photo insights and answers.

## Enterprise Features

- **CI/CD Pipeline** - Automated testing and deployment
- **Performance Monitoring** - Real-time metrics and health checks
- **API Documentation** - Swagger/OpenAPI integration
- **Dashboard** - Real-time system monitoring
- **Unit Testing** - Comprehensive test coverage
- **Code Quality** - Linting and formatting automation

## Technologies

- **AI/ML**: Google Cloud Vision API, OpenAI GPT-4, Sentence Transformers
- **Backend**: Python 3.11+, Flask, FastAPI
- **Frontend**: Streamlit, HTML/CSS/JS
- **DevOps**: GitHub Actions, Docker, Docker Compose
- **Monitoring**: Custom metrics collection, System health tracking
- **Testing**: Pytest, Coverage reporting

## Installation

```bash
git clone https://github.com/e1washere/photo-assistant.git
cd photo-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set up your API keys:

```bash
# OpenAI API Key
export OPENAI_API_KEY="your-openai-key"

# Google Cloud Credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

## Usage

### Command Line Interface

```bash
# Analyze an image
python main.py --image path/to/image.jpg

# Analyze image and answer a question
python main.py --image path/to/image.jpg --question "What objects do you see?"

# Run demo with sample image
python main.py --demo
```

### Web Interfaces

```bash
# Streamlit interface
python run_streamlit.py

# Flask API
python main.py --web
```

### API Documentation

Access Swagger documentation at: `http://localhost:5000/docs/`

## Project Structure

```
photo-assistant/
├── main.py                 # CLI and Flask entry point
├── run_streamlit.py        # Streamlit launcher
├── api_docs.py            # Swagger API documentation
├── dashboard.py           # Real-time monitoring dashboard
├── monitoring.py          # Performance monitoring system
├── cloud/                 # AI service integrations
│   ├── vision_api.py     # Google Cloud Vision client
│   └── llm_api.py        # OpenAI GPT-4 client
├── faq/                  # FAQ system
│   └── faq_handler.py    # Semantic search and Q&A
├── ui/                   # Web interfaces
│   ├── app.py           # Flask application
│   └── streamlit_app.py # Streamlit application
├── tests/                # Unit tests
│   └── test_vision_api.py
├── data/                 # Data files
│   └── faq.json         # FAQ database
├── static/               # Static assets
├── .github/workflows/    # CI/CD pipeline
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/upload` | POST | Upload and analyze image |
| `/ask` | POST | Ask questions about images |
| `/faq` | GET | Retrieve FAQ data |
| `/faq/search` | POST | Search FAQ questions |
| `/health` | GET | Health check endpoint |

### Example Usage

```bash
# Upload an image
curl -X POST -F "file=@image.jpg" http://localhost:5000/upload

# Ask a question about an uploaded image
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What objects do you see?", "filename": "uploaded_image.jpg"}' \
  http://localhost:5000/ask
```

## Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Image Analysis** | Object detection, OCR, scene classification | Google Cloud Vision API |
| **Natural Language Q&A** | Ask questions about images in plain English | OpenAI GPT-4 |
| **Semantic Search** | Find relevant FAQ answers using embeddings | Sentence Transformers |
| **Multiple Interfaces** | Streamlit UI, CLI, REST API | Flask + Streamlit |
| **Real-time Processing** | Instant analysis and response generation | Async processing |
| **Performance Monitoring** | System health and metrics tracking | Custom monitoring |
| **API Documentation** | Interactive API documentation | Swagger/OpenAPI |

## Development

### Code Quality

- **Type Hints**: All functions include comprehensive type annotations
- **Documentation**: Detailed docstrings for all public functions
- **Error Handling**: Robust error handling with graceful fallbacks
- **Testing**: Mock responses for development without API keys

### Running Tests

```bash
# Run all tests
python test_functionality.py

# Run unit tests with pytest
pytest tests/

# Run with coverage
pytest --cov=./ --cov-report=html
```

### Code Formatting

```bash
# Format code with Black
black .

# Lint code with Flake8
flake8 .
```

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

```bash
# Build and run with Docker
docker build -t photo-assistant .
docker run -p 5000:5000 photo-assistant

# Or use Docker Compose
docker-compose up -d
```

## Monitoring and Analytics

### Dashboard

Access the real-time monitoring dashboard:
```bash
python dashboard.py
```

### Metrics

The system collects:
- API call performance metrics
- System resource utilization
- Error rates and success rates
- Processing time statistics

### Health Checks

Monitor system health:
```bash
curl http://localhost:5000/health
```

## Limitations

- Requires internet connection for cloud services
- Maximum 16MB file size
- API rate limits apply
- Images processed by external services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please refer to the FAQ section in the application or create an issue in the repository. 