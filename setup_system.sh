#!/bin/bash

# Blood Test Analysis System - Setup Script

echo "🩸 Blood Test Analysis System Setup"
echo "==================================="

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "This script is designed for Linux systems."
    echo "Please install dependencies manually on other systems."
fi

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$python_version >= 3.8" | bc -l) != 1 ]]; then
    echo "Error: Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "Python version: $python_version ✓"

# Install system dependencies
echo ""
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y redis-server python3-venv python3-pip build-essential
elif command -v yum &> /dev/null; then
    sudo yum install -y redis python3-venv python3-pip gcc gcc-c++
elif command -v pacman &> /dev/null; then
    sudo pacman -S redis python-virtualenv python-pip base-devel
else
    echo "Unknown package manager. Please install Redis and build tools manually."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data uploads

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cat > .env << EOL
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./blood_test_analysis.db

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
EOL
    echo "⚠️  Please edit .env file and add your OpenAI API key!"
else
    echo ".env file already exists ✓"
fi

# Start Redis if not running
echo ""
echo "Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Starting Redis..."
    sudo systemctl start redis
    sleep 2
    
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "Failed to start Redis via systemctl. Trying manual start..."
        nohup redis-server > redis.log 2>&1 &
        sleep 2
    fi
fi

if redis-cli ping > /dev/null 2>&1; then
    echo "Redis is running ✓"
else
    echo "⚠️  Redis is not running. Please start it manually:"
    echo "   sudo systemctl start redis"
    echo "   or"
    echo "   redis-server"
fi

# Make scripts executable
chmod +x start_workers.sh
chmod +x setup_system.sh

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Start the workers: ./start_workers.sh"
echo "3. In another terminal, start the API: python main.py"
echo "4. Visit http://localhost:8000 to see the API"
echo "5. Visit http://localhost:5555 to see Flower monitoring"
echo ""
echo "For Docker deployment:"
echo "   docker-compose up -d"
echo ""
echo "Happy analyzing! 🔬" 