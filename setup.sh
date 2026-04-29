#!/bin/bash
# Setup script for Codeplex AI

set -e

echo "=========================================="
echo "Codeplex AI - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create directories
echo "Creating application directories..."
mkdir -p logs app tests output
echo "✓ Directories created"
echo ""

# Copy environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠ Please update .env with your API keys"
else
    echo "✓ .env file already exists"
fi
echo ""

echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update the .env file with your API keys"
echo "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo "3. Run 'make dev' to start the development server"
echo "4. Or run 'docker-compose up' to run with Docker"
echo ""

# Display API keys status
echo "API Keys Status:"
if grep -q "OPENAI_API_KEY=" .env; then
    if grep -q "OPENAI_API_KEY=your_" .env; then
        echo "⚠ OpenAI API Key: NOT SET"
    else
        echo "✓ OpenAI API Key: SET"
    fi
fi

if grep -q "ANTHROPIC_API_KEY=" .env; then
    if grep -q "ANTHROPIC_API_KEY=your_" .env; then
        echo "⚠ Anthropic API Key: NOT SET"
    else
        echo "✓ Anthropic API Key: SET"
    fi
fi

if grep -q "GOOGLE_API_KEY=" .env; then
    if grep -q "GOOGLE_API_KEY=your_" .env; then
        echo "⚠ Google API Key: NOT SET"
    else
        echo "✓ Google API Key: SET"
    fi
fi

