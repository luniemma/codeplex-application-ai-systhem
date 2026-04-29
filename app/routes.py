"""
API Routes Module - REST endpoints for Codeplex AI
"""
import logging
from flask import Blueprint, request, jsonify
from app.ai_services import (
    analyze_code, generate_code, chat as ai_chat,
    AIServiceFactory
)
from app.utils import validate_request, create_response

logger = logging.getLogger(__name__)

# Create blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api')
health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'codeplex-ai',
        'version': '1.0.0'
    }), 200


@api_bp.route('/models', methods=['GET'])
def list_models():
    """List available AI models"""
    try:
        providers = AIServiceFactory.get_available_providers()
        return create_response({
            'providers': providers,
            'count': len(providers)
        }, 200)
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        return create_response({'error': str(e)}, 500)


@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze code endpoint"""
    try:
        # Validate request
        if not request.json or 'code' not in request.json:
            return create_response({'error': 'Code is required'}, 400)
        
        code = request.json.get('code')
        provider = request.json.get('provider', 'openai')
        
        if not code:
            return create_response({'error': 'Code cannot be empty'}, 400)
        
        # Analyze code
        result = analyze_code(code, provider)
        return create_response(result, 200)
        
    except ValueError as e:
        logger.warning(f"Validation error in analyze: {str(e)}")
        return create_response({'error': str(e)}, 400)
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return create_response({'error': f'Analysis failed: {e}'}, 500)


@api_bp.route('/generate', methods=['POST'])
def generate():
    """Generate code endpoint"""
    try:
        # Validate request
        if not request.json or 'prompt' not in request.json:
            return create_response({'error': 'Prompt is required'}, 400)
        
        prompt = request.json.get('prompt')
        provider = request.json.get('provider', 'openai')
        
        if not prompt:
            return create_response({'error': 'Prompt cannot be empty'}, 400)
        
        # Generate code
        generated_code = generate_code(prompt, provider)
        return create_response({
            'provider': provider,
            'prompt': prompt,
            'generated_code': generated_code
        }, 200)
        
    except ValueError as e:
        logger.warning(f"Validation error in generate: {str(e)}")
        return create_response({'error': str(e)}, 400)
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        return create_response({'error': f'Code generation failed: {e}'}, 500)


@api_bp.route('/optimize', methods=['POST'])
def optimize():
    """Optimize code endpoint"""
    try:
        # Validate request
        if not request.json or 'code' not in request.json:
            return create_response({'error': 'Code is required'}, 400)
        
        code = request.json.get('code')
        provider = request.json.get('provider', 'openai')
        
        if not code:
            return create_response({'error': 'Code cannot be empty'}, 400)
        
        # Create optimization prompt
        prompt = f"""Analyze and optimize the following code for performance, readability, and best practices:

{code}

Provide:
1. Identified issues
2. Optimized version of the code
3. Explanation of changes
4. Performance improvements"""
        
        optimized = generate_code(prompt, provider)
        
        return create_response({
            'provider': provider,
            'original_code': code,
            'optimized_code': optimized
        }, 200)
        
    except ValueError as e:
        logger.warning(f"Validation error in optimize: {str(e)}")
        return create_response({'error': str(e)}, 400)
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        return create_response({'error': f'Code optimization failed: {e}'}, 500)


@api_bp.route('/chat', methods=['POST'])
def chat():
    """Chat with AI endpoint"""
    try:
        # Validate request
        if not request.json or 'messages' not in request.json:
            return create_response({'error': 'Messages are required'}, 400)
        
        messages = request.json.get('messages', [])
        provider = request.json.get('provider', 'openai')
        
        if not messages or not isinstance(messages, list):
            return create_response({'error': 'Messages must be a non-empty list'}, 400)
        
        # Chat with AI
        response = ai_chat(messages, provider)
        
        return create_response({
            'provider': provider,
            'messages': messages,
            'response': response
        }, 200)
        
    except ValueError as e:
        logger.warning(f"Validation error in chat: {str(e)}")
        return create_response({'error': str(e)}, 400)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return create_response({'error': f'Chat failed: {e}'}, 500)


@api_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """Batch analyze multiple code snippets"""
    try:
        if not request.json or 'codes' not in request.json:
            return create_response({'error': 'Codes array is required'}, 400)
        
        codes = request.json.get('codes', [])
        provider = request.json.get('provider', 'openai')
        
        if not codes or not isinstance(codes, list):
            return create_response({'error': 'Codes must be a non-empty list'}, 400)
        
        results = []
        for idx, code in enumerate(codes):
            try:
                result = analyze_code(code, provider)
                results.append({
                    'index': idx,
                    'status': 'success',
                    'data': result
                })
            except Exception as e:
                results.append({
                    'index': idx,
                    'status': 'error',
                    'error': str(e)
                })
        
        return create_response({
            'provider': provider,
            'total': len(codes),
            'results': results
        }, 200)
        
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        return create_response({'error': f'Batch analysis failed: {e}'}, 500)


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_response({'error': 'Endpoint not found'}, 404)


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return create_response({'error': 'Internal server error'}, 500)

