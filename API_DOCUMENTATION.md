# Codeplex AI - API Documentation

## Overview

Codeplex AI is a comprehensive Python application that provides AI-powered code analysis, generation, and optimization services. It integrates with multiple AI providers including OpenAI, Anthropic, and Google.

## Base URL

```
http://localhost:8000
https://api.codeplex.ai (production)
```

## Authentication

Currently, the API doesn't require authentication. This should be implemented in production with JWT tokens.

## Response Format

All responses follow this format:

```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    // Response data
  }
}
```

## Endpoints

### 1. Health Check

Check if the service is running.

**Request:**
```
GET /health
```

**Response:**
```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    "status": "healthy",
    "service": "codeplex-ai",
    "version": "1.0.0"
  }
}
```

### 2. List Available Models

Get list of available AI providers.

**Request:**
```
GET /api/models
```

**Response:**
```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    "providers": ["openai", "anthropic", "google"],
    "count": 3
  }
}
```

### 3. Analyze Code

Analyze code and get detailed feedback.

**Request:**
```
POST /api/analyze
Content-Type: application/json

{
  "code": "def hello():\n    print('Hello, World!')",
  "provider": "openai"
}
```

**Response:**
```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    "provider": "openai",
    "analysis": "This is a simple Python function that prints 'Hello, World!' to the console...",
    "tokens_used": 150
  }
}
```

### 4. Generate Code

Generate code based on a prompt.

**Request:**
```
POST /api/generate
Content-Type: application/json

{
  "prompt": "Write a Python function to calculate the factorial of a number",
  "provider": "openai"
}
```

**Response:**
```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    "provider": "openai",
    "prompt": "Write a Python function to calculate the factorial of a number",
    "generated_code": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)"
  }
}
```

### 5. Optimize Code

Optimize code for performance and readability.

**Request:**
```
POST /api/optimize
Content-Type: application/json

{
  "code": "def slow_function():\n    result = []\n    for i in range(1000):\n        for j in range(1000):\n            result.append(i*j)\n    return result",
  "provider": "openai"
}
```

**Response:**
```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    "provider": "openai",
    "original_code": "def slow_function()...",
    "optimized_code": "def optimized_function():\n    return [i*j for i in range(1000) for j in range(1000)]"
  }
}
```

### 6. Chat with AI

Have a conversation with the AI.

**Request:**
```
POST /api/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "How do I use async/await in Python?"}
  ],
  "provider": "openai"
}
```

**Response:**
```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    "provider": "openai",
    "messages": [...],
    "response": "Async/await in Python is used for asynchronous programming..."
  }
}
```

### 7. Batch Analyze

Analyze multiple code snippets at once.

**Request:**
```
POST /api/batch-analyze
Content-Type: application/json

{
  "codes": [
    "print('hello')",
    "def foo(): pass"
  ],
  "provider": "openai"
}
```

**Response:**
```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 200,
  "data": {
    "provider": "openai",
    "total": 2,
    "results": [
      {
        "index": 0,
        "status": "success",
        "data": {"analysis": "..."}
      },
      {
        "index": 1,
        "status": "success",
        "data": {"analysis": "..."}
      }
    ]
  }
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes:

```json
{
  "timestamp": "2024-04-28T10:00:00.000000",
  "status_code": 400,
  "data": {
    "error": "Code is required"
  }
}
```

### Common Status Codes

- `200` - Success
- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Rate limiting can be enabled in `.env`. Default limits are configurable.

## Authentication (Future)

JWT token authentication will be implemented. Include token in header:

```
Authorization: Bearer <token>
```

## Examples

### Using cURL

```bash
# Health check
curl -X GET http://localhost:8000/health

# Analyze code
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")", "provider": "openai"}'

# Generate code
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write hello world function", "provider": "openai"}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Analyze code
payload = {
    "code": "print('hello')",
    "provider": "openai"
}
response = requests.post(f"{BASE_URL}/api/analyze", json=payload)
print(response.json())

# Generate code
payload = {
    "prompt": "Write a function to add two numbers",
    "provider": "openai"
}
response = requests.post(f"{BASE_URL}/api/generate", json=payload)
print(response.json())
```

### Using JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// Analyze code
async function analyzeCode(code) {
  const response = await fetch(`${BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      code: code,
      provider: 'openai'
    })
  });
  return response.json();
}

// Generate code
async function generateCode(prompt) {
  const response = await fetch(`${BASE_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      provider: 'openai'
    })
  });
  return response.json();
}
```

## Configuration

See `.env.example` for all available configuration options.

## Support

For issues and questions, please open an issue on GitHub or contact support.

