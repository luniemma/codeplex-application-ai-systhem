# Codeplex AI - Quick Start Guide

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)
- API keys for AI services:
  - OpenAI API key
  - Anthropic (Claude) API key (optional)
  - Google API key (optional)

## Installation

### Option 1: Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/codeplex.ai.git
cd codeplex.ai
```

2. **Run setup script:**

On Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

On Windows:
```bash
setup.bat
```

3. **Activate virtual environment:**

On Linux/Mac:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

4. **Create and configure .env file:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run development server:**
```bash
make dev
```

Or with Flask directly:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Option 2: Docker

1. **Create .env file:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. **Production deployment:**
```bash
docker-compose up -d
```

3. **Development deployment:**
```bash
docker-compose -f docker-compose.dev.yml up
```

## First Request

Test the API with a health check:

```bash
curl http://localhost:8000/health
```

Response:
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

## Analyze Code

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello, World!\")",
    "provider": "openai"
  }'
```

## Generate Code

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to calculate factorial",
    "provider": "openai"
  }'
```

## Run Tests

```bash
make test
```

Or with coverage:
```bash
make test-cov
```

## View Documentation

- API Documentation: `API_DOCUMENTATION.md`
- Deployment Guide: `DEPLOYMENT.md`

## Useful Commands

```bash
# Start development server
make dev

# Start production server
make prod

# Run tests
make test

# Run tests with coverage
make test-cov

# Code linting
make lint

# Format code
make format

# Docker commands
make docker-build      # Build images
make docker-up         # Start containers
make docker-down       # Stop containers
make docker-logs       # View logs
make docker-dev        # Start development containers

# Database commands
make db-migrate        # Run migrations
make db-makemigrations # Create migrations
```

## Troubleshooting

### API Not Responding

1. Check if server is running:
```bash
curl http://localhost:8000/health
```

2. Check logs:
```bash
# Local
tail -f logs/codeplex.log

# Docker
docker-compose logs -f codeplex-api
```

### API Key Errors

1. Ensure `.env` file exists and is configured
2. Verify API keys are valid
3. Check API key format in `.env` file

### Connection to Redis/PostgreSQL Failed

1. Ensure Redis and PostgreSQL are running
2. Check connection strings in `.env`
3. Verify ports are not in use

### Docker Issues

1. Build image:
```bash
docker build -t codeplex-ai .
```

2. Check Docker logs:
```bash
docker logs codeplex-ai-api
```

## Next Steps

1. Configure your API keys in `.env`
2. Read the API documentation
3. Deploy to your chosen platform
4. Set up monitoring and logging
5. Configure CI/CD pipeline

## Support

- Documentation: Read README.md and API_DOCUMENTATION.md
- Issues: Open an issue on GitHub
- Questions: Contact the development team

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude Documentation](https://www.anthropic.com/docs)
- [Google Generative AI Documentation](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)

