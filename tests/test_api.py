"""
Test Suite for Codeplex AI
"""
from unittest.mock import patch

import pytest

from main import create_app


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['data']['status'] == 'healthy'


class TestModelsEndpoint:
    """Test models endpoint"""

    def test_list_models(self, client):
        """Test listing available models"""
        response = client.get('/api/models')
        assert response.status_code == 200
        assert 'providers' in response.json['data']


class TestAnalyzeEndpoint:
    """Test code analysis endpoint"""

    def test_analyze_missing_code(self, client):
        """Test analysis with missing code"""
        response = client.post('/api/analyze', json={})
        assert response.status_code == 400
        assert 'error' in response.json['data']

    def test_analyze_empty_code(self, client):
        """Test analysis with empty code"""
        response = client.post('/api/analyze', json={'code': ''})
        assert response.status_code == 400

    @patch('app.routes.analyze_code')
    def test_analyze_success(self, mock_analyze, client):
        """Test successful analysis"""
        mock_analyze.return_value = {
            'provider': 'openai',
            'analysis': 'Test analysis',
            'tokens_used': 100
        }

        response = client.post('/api/analyze', json={
            'code': 'print("hello")',
            'provider': 'openai'
        })

        assert response.status_code == 200
        assert 'analysis' in response.json['data']


class TestGenerateEndpoint:
    """Test code generation endpoint"""

    def test_generate_missing_prompt(self, client):
        """Test generation with missing prompt"""
        response = client.post('/api/generate', json={})
        assert response.status_code == 400

    def test_generate_empty_prompt(self, client):
        """Test generation with empty prompt"""
        response = client.post('/api/generate', json={'prompt': ''})
        assert response.status_code == 400

    @patch('app.routes.generate_code')
    def test_generate_success(self, mock_generate, client):
        """Test successful code generation"""
        mock_generate.return_value = 'def hello():\n    print("Hello, World!")'

        response = client.post('/api/generate', json={
            'prompt': 'Write a function to print hello',
            'provider': 'openai'
        })

        assert response.status_code == 200
        assert 'generated_code' in response.json['data']


class TestOptimizeEndpoint:
    """Test code optimization endpoint"""

    def test_optimize_missing_code(self, client):
        """Test optimization with missing code"""
        response = client.post('/api/optimize', json={})
        assert response.status_code == 400

    @patch('app.routes.generate_code')
    def test_optimize_success(self, mock_generate, client):
        """Test successful code optimization"""
        mock_generate.return_value = 'optimized code'

        response = client.post('/api/optimize', json={
            'code': 'unoptimized code',
            'provider': 'openai'
        })

        assert response.status_code == 200
        assert 'optimized_code' in response.json['data']


class TestChatEndpoint:
    """Test chat endpoint"""

    def test_chat_missing_messages(self, client):
        """Test chat with missing messages"""
        response = client.post('/api/chat', json={})
        assert response.status_code == 400

    def test_chat_empty_messages(self, client):
        """Test chat with empty messages"""
        response = client.post('/api/chat', json={'messages': []})
        assert response.status_code == 400

    @patch('app.routes.ai_chat')
    def test_chat_success(self, mock_chat, client):
        """Test successful chat"""
        mock_chat.return_value = 'Chat response'

        response = client.post('/api/chat', json={
            'messages': [
                {'role': 'user', 'content': 'Hello'}
            ],
            'provider': 'openai'
        })

        assert response.status_code == 200
        assert 'response' in response.json['data']


class TestBatchAnalyzeEndpoint:
    """Test batch analysis endpoint"""

    def test_batch_analyze_missing_codes(self, client):
        """Test batch analysis with missing codes"""
        response = client.post('/api/batch-analyze', json={})
        assert response.status_code == 400

    @patch('app.routes.analyze_code')
    def test_batch_analyze_success(self, mock_analyze, client):
        """Test successful batch analysis"""
        mock_analyze.return_value = {'analysis': 'Test'}

        response = client.post('/api/batch-analyze', json={
            'codes': [
                'code1',
                'code2'
            ],
            'provider': 'openai'
        })

        assert response.status_code == 200
        assert 'results' in response.json['data']


class TestErrorHandling:
    """Test error handling"""

    def test_not_found(self, client):
        """Test 404 error"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Test invalid JSON"""
        response = client.post(
            '/api/analyze',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 422]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

