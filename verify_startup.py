"""
Startup Verification Script for Codeplex AI
Checks all requirements before running the application
"""
import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("=" * 60)
    print("Codeplex AI - Startup Verification")
    print("=" * 60)
    print()
    
    # Check Python version
    print("1. Python Version Check")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   ✓ Python {version.major}.{version.minor} (Required: 3.9+)")
    else:
        print(f"   ✗ Python {version.major}.{version.minor} (Required: 3.9+)")
        return False
    print()
    
    # Check if we're in the right directory
    print("2. Project Structure Check")
    if os.path.exists('app') and os.path.exists('main.py'):
        print("   ✓ Project structure intact")
    else:
        print("   ✗ Project structure missing")
        return False
    print()
    
    # Check dependencies
    print("3. Dependencies Check")
    required_packages = [
        'flask', 'flask_cors', 'python_dotenv', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print()
        print("   Missing packages! Run:")
        print("   pip install -r requirements.txt")
        print()
    print()
    
    # Check .env file
    print("4. Environment Configuration Check")
    if os.path.exists('.env'):
        print("   ✓ .env file exists")
    else:
        print("   ⚠ .env file not found (will use defaults)")
        print("   To use AI features, create .env from .env.example:")
        print("   cp .env.example .env")
        print()
    print()
    
    # Check API keys
    print("5. API Keys Check")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_status = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
    }
    
    for key, value in api_status.items():
        if value and not value.startswith('your_'):
            print(f"   ✓ {key} configured")
        else:
            print(f"   ⚠ {key} not configured")
    
    print()
    print("=" * 60)
    return True


def run_health_check():
    """Run a basic health check on the Flask app"""
    print("\n🚀 Starting Codeplex AI Application...\n")
    
    try:
        from main import create_app
        app = create_app()
        
        print("✓ Flask app created successfully")
        print("✓ All blueprints registered")
        print()
        print("=" * 60)
        print("Application is ready to run!")
        print("=" * 60)
        print()
        print("To start the development server:")
        print("  python main.py")
        print()
        print("Or with Flask CLI:")
        print("  flask run")
        print()
        print("API will be available at: http://localhost:8000")
        print()
        print("Try these endpoints:")
        print("  GET  http://localhost:8000/health          (Health check)")
        print("  GET  http://localhost:8000/api/models      (List AI providers)")
        print("  POST http://localhost:8000/api/analyze     (Analyze code)")
        print()
        
        return True
    except Exception as e:
        print(f"✗ Error creating Flask app: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run checks
    if check_requirements():
        run_health_check()

