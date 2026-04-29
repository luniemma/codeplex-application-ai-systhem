# Codeplex AI System
# Advanced AI-powered application for code analysis and generation

A comprehensive AI system that leverages multiple language models for intelligent code analysis, generation, and optimization.

## Features

- 🤖 Multi-AI Integration (OpenAI, Anthropic, Google)
- 📊 Advanced Code Analysis
- 💡 Intelligent Code Generation
- 🔍 Real-time Processing
- 📈 Performance Analytics
- 🔐 Secure API Endpoints
- 🐳 Docker Support
- 🧪 Comprehensive Testing

## Installation

### Prerequisites
- Python 3.9+
- Docker (optional)
- API keys for AI services (OpenAI, Anthropic, Google)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/codeplex.ai.git
cd codeplex.ai
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
python main.py
```

## Docker Setup

Build and run using Docker:
```bash
docker build -t codeplex-ai .
docker run -p 8000:8000 --env-file .env codeplex-ai
```

## API Endpoints

- `POST /api/analyze` - Analyze code
- `POST /api/generate` - Generate code
- `POST /api/optimize` - Optimize code
- `GET /api/health` - Health check
- `POST /api/chat` - Chat with AI
- `GET /api/models` - List available models

## Configuration

See `.env.example` for available configuration options.

## Testing

Run tests:
```bash
pytest tests/
pytest tests/ --cov=app
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

