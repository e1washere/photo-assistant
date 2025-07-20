"""
API Documentation for Photo Assistant

Comprehensive API documentation using Flask-RESTX and Swagger UI.
"""

from flask import Flask
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
import os
import tempfile
from pathlib import Path

# Import our services
from cloud.vision_api import VisionAPI
from cloud.llm_api import LLMAPI
from faq.faq_handler import FAQHandler

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize API with Swagger documentation
api = Api(
    app,
    version='1.0',
    title='Photo Assistant API',
    description='AI-powered image analysis and FAQ system',
    doc='/docs/',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key'
        }
    }
)

# Initialize services
vision_api = VisionAPI()
llm_api = LLMAPI()
faq_handler = FAQHandler()

# Define namespaces
ns_images = api.namespace('images', description='Image analysis operations')
ns_faq = api.namespace('faq', description='FAQ operations')
ns_health = api.namespace('health', description='Health check operations')

# Define models for Swagger documentation
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Image file to analyze')

question_model = api.model('Question', {
    'question': fields.String(required=True, description='Question to ask about the image'),
    'filename': fields.String(required=True, description='Filename of uploaded image')
})

faq_question_model = api.model('FAQQuestion', {
    'question': fields.String(required=True, description='FAQ question to search for')
})

analysis_response_model = api.model('AnalysisResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'filename': fields.String(description='Uploaded filename'),
    'vision_description': fields.String(description='Vision API analysis description'),
    'llm_description': fields.String(description='LLM enhanced description'),
    'labels': fields.List(fields.String, description='Detected labels'),
    'tags': fields.List(fields.String, description='Generated tags'),
    'processing_time': fields.Float(description='Processing time in seconds')
})

faq_response_model = api.model('FAQResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'answer': fields.String(description='FAQ answer'),
    'similar_questions': fields.List(fields.Raw, description='Similar questions found'),
    'confidence': fields.Float(description='Answer confidence score')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message'),
    'code': fields.Integer(description='HTTP status code')
})

@ns_images.route('/upload')
class ImageUpload(Resource):
    @api.doc('upload_image')
    @api.expect(upload_parser)
    @api.marshal_with(analysis_response_model, code=200)
    @api.response(400, 'Invalid file', error_model)
    @api.response(500, 'Processing error', error_model)
    def post(self):
        """Upload and analyze an image"""
        import time
        start_time = time.time()
        
        try:
            args = upload_parser.parse_args()
            uploaded_file = args['file']
            
            if not uploaded_file:
                api.abort(400, 'No file provided')
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            if not uploaded_file.filename.lower().endswith(tuple(allowed_extensions)):
                api.abort(400, 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP')
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                uploaded_file.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            try:
                # Analyze image
                vision_description, labels = vision_api.analyze_image(tmp_path)
                llm_description, tags = llm_api.generate_description_tags(vision_description)
                
                processing_time = time.time() - start_time
                
                return {
                    'success': True,
                    'filename': uploaded_file.filename,
                    'vision_description': vision_description,
                    'llm_description': llm_description,
                    'labels': labels,
                    'tags': tags,
                    'processing_time': round(processing_time, 2)
                }
            
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            api.abort(500, f'Processing error: {str(e)}')

@ns_images.route('/ask')
class ImageQuestion(Resource):
    @api.doc('ask_question')
    @api.expect(question_model)
    @api.marshal_with(faq_response_model, code=200)
    @api.response(400, 'Invalid request', error_model)
    @api.response(404, 'Image not found', error_model)
    def post(self):
        """Ask a question about an uploaded image"""
        try:
            data = api.payload
            question = data.get('question', '')
            filename = data.get('filename', '')
            
            if not question or not filename:
                api.abort(400, 'Question and filename required')
            
            # For demo purposes, we'll use FAQ search
            answer = faq_handler.answer_question(question)
            similar_questions = faq_handler.get_similar_questions(question, top_k=3)
            
            return {
                'success': True,
                'answer': answer,
                'similar_questions': [
                    {
                        'question': qa[0],
                        'answer': qa[1],
                        'similarity': round(qa[2], 3)
                    }
                    for qa in similar_questions
                ],
                'confidence': 0.85
            }
            
        except Exception as e:
            api.abort(500, f'Error processing question: {str(e)}')

@ns_faq.route('/search')
class FAQSearch(Resource):
    @api.doc('search_faq')
    @api.expect(faq_question_model)
    @api.marshal_with(faq_response_model, code=200)
    @api.response(400, 'Invalid request', error_model)
    def post(self):
        """Search FAQ for answers"""
        try:
            data = api.payload
            question = data.get('question', '')
            
            if not question:
                api.abort(400, 'Question required')
            
            answer = faq_handler.answer_question(question)
            similar_questions = faq_handler.get_similar_questions(question, top_k=5)
            
            return {
                'success': True,
                'answer': answer,
                'similar_questions': [
                    {
                        'question': qa[0],
                        'answer': qa[1],
                        'similarity': round(qa[2], 3)
                    }
                    for qa in similar_questions
                ],
                'confidence': 0.9
            }
            
        except Exception as e:
            api.abort(500, f'Error searching FAQ: {str(e)}')

@ns_faq.route('/list')
class FAQList(Resource):
    @api.doc('list_faq')
    @api.marshal_list_with(faq_question_model, code=200)
    def get(self):
        """Get list of all FAQ questions"""
        try:
            all_questions = faq_handler.get_all_questions()
            return [
                {'question': qa[0], 'answer': qa[1]}
                for qa in all_questions
            ]
        except Exception as e:
            api.abort(500, f'Error retrieving FAQ: {str(e)}')

@ns_health.route('/')
class HealthCheck(Resource):
    @api.doc('health_check')
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'services': {
                'vision_api': 'operational',
                'llm_api': 'operational',
                'faq_handler': 'operational'
            }
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 