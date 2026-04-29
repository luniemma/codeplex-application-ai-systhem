"""
Data Models for Codeplex AI
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class AnalysisRequest:
    """Model for code analysis request"""
    code: str
    provider: str = 'openai'
    language: str = 'python'
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


@dataclass
class AnalysisResult:
    """Model for code analysis result"""
    code: str
    provider: str
    analysis: str
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: float = 0.0
    tokens_used: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GenerationRequest:
    """Model for code generation request"""
    prompt: str
    provider: str = 'openai'
    language: str = 'python'
    constraints: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


@dataclass
class GenerationResult:
    """Model for code generation result"""
    prompt: str
    provider: str
    generated_code: str
    language: str = 'python'
    tokens_used: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatMessage:
    """Model for chat message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatRequest:
    """Model for chat request"""
    messages: List[ChatMessage]
    provider: str = 'openai'
    temperature: float = 0.7
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatResponse:
    """Model for chat response"""
    messages: List[ChatMessage]
    response: str
    provider: str
    tokens_used: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class APIError:
    """Model for API errors"""
    error: str
    error_code: str
    details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class APIResponse:
    """Model for API responses"""
    status: str  # 'success', 'error'
    data: Any = None
    error: Optional[APIError] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ModelRegistry:
    """Registry for data models"""
    
    _models = {
        'AnalysisRequest': AnalysisRequest,
        'AnalysisResult': AnalysisResult,
        'GenerationRequest': GenerationRequest,
        'GenerationResult': GenerationResult,
        'ChatMessage': ChatMessage,
        'ChatRequest': ChatRequest,
        'ChatResponse': ChatResponse,
        'APIError': APIError,
        'APIResponse': APIResponse,
    }
    
    @staticmethod
    def get_model(model_name: str):
        """Get model by name"""
        return ModelRegistry._models.get(model_name)
    
    @staticmethod
    def get_all_models():
        """Get all registered models"""
        return list(ModelRegistry._models.keys())

