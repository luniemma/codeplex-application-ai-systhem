# Codeplex AI - Project Structure

```
codeplex-ai/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── ai_services.py           # AI provider integrations
│   ├── routes.py                # API endpoints
│   ├── utils.py                 # Utility functions
│   ├── models.py                # Data models
│   ├── database.py              # Database setup
│   └── cache.py                 # Caching functionality
├── tests/
│   ├── __init__.py
│   └── test_api.py              # API tests
├── main.py                      # Application entry point
├── gunicorn_config.py           # Gunicorn server configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Production Docker image
├── Dockerfile.dev               # Development Docker image
├── docker-compose.yml           # Production Docker Compose
├── docker-compose.dev.yml       # Development Docker Compose
├── nginx.conf                   # Nginx reverse proxy config
├── Makefile                     # Make commands
├── setup.sh                     # Unix setup script
├── setup.bat                    # Windows setup script
├── README.md                    # Project documentation
├── QUICKSTART.md               # Quick start guide
├── API_DOCUMENTATION.md        # API reference
└── DEPLOYMENT.md               # Deployment guide
```

## Directory Descriptions

### `/app/`
Main application package containing:
- **config.py**: Configuration management and environment variables
- **ai_services.py**: Multi-provider AI integration (OpenAI, Anthropic, Google)
- **routes.py**: Flask blueprints and API endpoints
- **utils.py**: Helper functions, decorators, and utilities
- **models.py**: Data classes and models
- **database.py**: Database initialization and management
- **cache.py**: Redis caching implementation

### `/tests/`
Test suite:
- **test_api.py**: Comprehensive API endpoint tests

### Root Directory
- **main.py**: Flask app creation and entry point
- **gunicorn_config.py**: Production server configuration
- **Dockerfile**: Multi-stage production image
- **Dockerfile.dev**: Development image with hot reload
- **.env.example**: Template for environment variables
- **Makefile**: Build and deployment automation
- **docker-compose.yml**: Production services orchestration
- **docker-compose.dev.yml**: Development environment setup

## File Descriptions

### Core Application Files

#### `main.py` (Entry Point)
- Creates Flask application
- Registers blueprints
- Configures CORS
- Main server startup

#### `app/config.py`
- Environment variable management
- Configuration dataclass
- Settings for all modules

#### `app/ai_services.py`
- Abstract AI provider interface
- OpenAI implementation
- Anthropic (Claude) implementation
- Google Generative AI implementation
- Service factory pattern
- Helper functions for code analysis and generation

#### `app/routes.py`
- REST API endpoints
- Request validation
- Error handling
- Health checks
- Code analysis endpoints
- Code generation endpoints
- Code optimization endpoints
- Chat endpoints
- Batch processing endpoints

#### `app/utils.py`
- Response formatting
- Input validation decorators
- Caching decorators
- Error handling utilities
- Performance measurement
- Request logging
- Data models for analysis results

#### `app/models.py`
- Request/response data models
- Analysis and generation models
- Chat message models
- Model registry

#### `app/database.py`
- SQLAlchemy setup
- Session management
- Database initialization
- Migration support

#### `app/cache.py`
- Redis cache client
- Cache decorators
- In-memory cache fallback
- Cache invalidation methods

### Docker Files

#### `Dockerfile`
- Multi-stage build for optimization
- Python 3.11-slim base
- Production-ready setup
- Non-root user
- Health checks
- Gunicorn entry point

#### `Dockerfile.dev`
- Development-focused image
- Flask development server
- Hot reload support
- Debug tools

### Configuration Files

#### `docker-compose.yml`
- Codeplex API service
- PostgreSQL database
- Redis cache
- Nginx reverse proxy
- Volume management
- Health checks

#### `docker-compose.dev.yml`
- Simplified development setup
- Volume mounting for live reload
- Single shared network

#### `nginx.conf`
- Reverse proxy configuration
- SSL/TLS setup
- Security headers
- Gzip compression
- API routing

### Automation Files

#### `Makefile`
Common commands for:
- Installation and setup
- Development and production runs
- Testing with coverage
- Code formatting and linting
- Docker operations
- Database migrations

#### `setup.sh` / `setup.bat`
Automated setup scripts for:
- Python environment setup
- Dependency installation
- Directory creation
- Configuration file generation

#### `gunicorn_config.py`
Production server configuration:
- Worker processes
- Timeouts
- Logging
- SSL setup

### Documentation Files

#### `README.md`
- Project overview
- Features
- Installation instructions
- Docker setup
- API endpoints

#### `QUICKSTART.md`
- Prerequisites
- Installation steps
- First requests
- Troubleshooting
- Useful commands

#### `API_DOCUMENTATION.md`
- Complete API reference
- Endpoint descriptions
- Request/response examples
- Error codes
- Usage examples

#### `DEPLOYMENT.md`
- Pre-deployment checklist
- Deployment strategies
- Cloud provider guides
- Security hardening
- Monitoring setup
- Scaling considerations

#### `.env.example`
- All configurable environment variables
- Default values
- AI provider keys
- Database URLs
- Logging settings

## Technology Stack

### Backend Framework
- Flask 2.3.3
- Gunicorn for production

### AI Integrations
- OpenAI 0.27.8
- Anthropic (Claude) 0.7.1
- Google Generative AI 0.3.0

### Database & Caching
- PostgreSQL (via psycopg2)
- Redis (via redis-py)
- SQLAlchemy ORM

### ML/Data Science
- NumPy, Pandas, Scikit-learn
- TensorFlow, PyTorch
- Transformers

### Testing & Quality
- Pytest
- Pytest-cov

### DevOps
- Docker & Docker Compose
- Nginx
- Gunicorn

## Getting Started

1. **Local Development:**
   ```bash
   chmod +x setup.sh  # On Windows: setup.bat
   ./setup.sh
   source venv/bin/activate
   make dev
   ```

2. **Docker Development:**
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

3. **Production Deployment:**
   ```bash
   docker-compose up -d
   ```

## Key Features

✅ Multi-AI provider support
✅ Code analysis and generation
✅ Batch processing capabilities
✅ Comprehensive API documentation
✅ Docker containerization
✅ Production-ready setup
✅ Testing framework
✅ Caching and optimization
✅ Security best practices
✅ Monitoring and logging

## Environment Variables

See `.env.example` for complete list. Key variables:

- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google API key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ENVIRONMENT` - dev/staging/production
- `DEBUG` - Debug mode flag

## API Endpoints

- `GET /health` - Health check
- `GET /api/models` - List available providers
- `POST /api/analyze` - Analyze code
- `POST /api/generate` - Generate code
- `POST /api/optimize` - Optimize code
- `POST /api/chat` - Chat with AI
- `POST /api/batch-analyze` - Batch analyze

## Development Commands

```bash
make install          # Install dependencies
make dev             # Run dev server
make prod            # Run prod server
make test            # Run tests
make lint            # Lint code
make format          # Format code
make docker-build    # Build Docker image
make docker-up       # Start Docker
make docker-down     # Stop Docker
```

## Next Steps

1. Configure API keys in `.env`
2. Review API documentation
3. Customize AI provider configurations
4. Set up monitoring and logging
5. Deploy to your infrastructure

See `QUICKSTART.md` for detailed setup instructions.

