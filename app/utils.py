"""
Utilities Module - Helper functions for Codeplex AI
"""
import json
import logging
from typing import Dict, Any, Tuple
from datetime import datetime
from functools import wraps
from flask import jsonify, request

logger = logging.getLogger(__name__)


def create_response(data: Dict[str, Any], status_code: int) -> Tuple:
    """Create a standardized JSON response"""
    response = {
        'timestamp': datetime.utcnow().isoformat(),
        'status_code': status_code,
        'data': data
    }
    return jsonify(response), status_code


def validate_request(required_fields: list):
    """Decorator to validate request payload"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                return create_response({'error': 'Request must be JSON'}, 400)
            
            for field in required_fields:
                if field not in request.json:
                    return create_response(
                        {'error': f'Missing required field: {field}'}, 
                        400
                    )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_request(f):
    """Decorator to log incoming requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Request: {request.method} {request.path}")
        if request.json:
            # Log without sensitive data
            data = request.json.copy()
            if 'api_key' in data:
                data['api_key'] = '***'
            logger.debug(f"Payload: {json.dumps(data)}")
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(max_requests: int = 100, time_window: int = 3600):
    """Rate limiting decorator (requires caching)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Placeholder for rate limiting logic
            # Would require Redis or similar
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cache_result(ttl: int = 3600):
    """Caching decorator (requires caching)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Placeholder for caching logic
            # Would require Redis or similar
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_errors(f):
    """Error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return create_response({'error': str(e)}, 400)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return create_response({'error': 'Internal server error'}, 500)
    return decorated_function


def sanitize_input(text: str, max_length: int = 100000) -> str:
    """Sanitize user input"""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    if len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")
    
    return text.strip()


def format_code_for_display(code: str, language: str = 'python') -> str:
    """Format code for display"""
    return f"```{language}\n{code}\n```"


def extract_code_blocks(text: str) -> list:
    """Extract code blocks from text"""
    import re
    pattern = r'```(?:[\w]*\n)?(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def estimate_token_count(text: str) -> int:
    """Rough estimation of token count (OpenAI tokenizer)"""
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4


def get_client_ip() -> str:
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def measure_performance(f):
    """Measure function execution time"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import time
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{f.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return decorated_function


class CodeAnalysisResult:
    """Result object for code analysis"""
    
    def __init__(self, code: str, provider: str):
        self.code = code
        self.provider = provider
        self.issues = []
        self.suggestions = []
        self.score = 0
    
    def add_issue(self, issue: str, severity: str = 'medium'):
        """Add an issue"""
        self.issues.append({'issue': issue, 'severity': severity})
    
    def add_suggestion(self, suggestion: str, priority: str = 'medium'):
        """Add a suggestion"""
        self.suggestions.append({'suggestion': suggestion, 'priority': priority})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'provider': self.provider,
            'code': self.code,
            'issues': self.issues,
            'suggestions': self.suggestions,
            'score': self.score
        }


class CodeGenerationRequest:
    """Request object for code generation"""
    
    def __init__(self, prompt: str, language: str = 'python', provider: str = 'openai'):
        self.prompt = prompt
        self.language = language
        self.provider = provider
        self.constraints = []
    
    def add_constraint(self, constraint: str):
        """Add a constraint"""
        self.constraints.append(constraint)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'prompt': self.prompt,
            'language': self.language,
            'provider': self.provider,
            'constraints': self.constraints
        }

