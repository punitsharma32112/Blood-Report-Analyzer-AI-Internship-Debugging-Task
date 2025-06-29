\#!/bin/bash

# Blood Test Analyzer - Environment Setup Script

echo "🔬 Initializing Blood Test Analyzer Setup"
echo "========================================="

# Ensure Linux system

if \[\[ "\$OSTYPE" != "linux-gnu"\* ]]; then
echo "⚠️ This script is tailored for Linux environments."
echo "    Manual setup may be required on your OS."
fi

# Verify Python version

python\_version=\$(python3 --version 2>&1 | grep -oE '\[0-9]+.\[0-9]+')
if \[\[ \$(echo "\$python\_version >= 3.8" | bc -l) != 1 ]]; then
echo "❌ Python 3.8+ is required. Detected: \$python\_version"
exit 1
else
echo "✅ Python version \$python\_version is supported."
fi

# Install base system dependencies

echo "\n📦 Installing system packages..."
if command -v apt-get &> /dev/null; then
sudo apt-get update
sudo apt-get install -y redis-server python3-venv python3-pip build-essential
elif command -v yum &> /dev/null; then
sudo yum install -y redis python3-venv python3-pip gcc gcc-c++
elif command -v pacman &> /dev/null; then
sudo pacman -S --noconfirm redis python-virtualenv python-pip base-devel
else
echo "⚠️ Unknown package manager. Please install Redis, pip, and venv manually."
fi

# Create virtual environment if missing

if \[ ! -d "venv" ]; then
echo "\n🧪 Setting up virtual environment..."
python3 -m venv venv
fi

# Activate venv

echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install project dependencies

echo "\n📚 Installing Python requirements..."
pip install -r requirements.txt

# Setup necessary folders

echo "\n📁 Creating directories: data/, uploads/"
mkdir -p data uploads

# Generate default .env if absent

if \[ ! -f ".env" ]; then
echo "\n⚙️ Creating .env configuration file..."
cat > .env << EOL

# OpenAI API Configuration

OPENAI\_API\_KEY=your\_openai\_api\_key\_here

# Database Configuration

DATABASE\_URL=sqlite:///./blood\_test\_analysis.db

# Redis Configuration

REDIS\_URL=redis\://localhost:6379/0

# Application Settings

DEBUG=True
LOG\_LEVEL=INFO
EOL
echo "⚠️ Please update your OpenAI API key in .env!"
else
echo "✅ .env file found. Skipping creation."
fi

# Redis check and start

echo "\n🧠 Checking Redis status..."
if ! redis-cli ping > /dev/null 2>&1; then
echo "🛠 Starting Redis service..."
sudo systemctl start redis
sleep 2
if ! redis-cli ping > /dev/null 2>&1; then
echo "⚠️ systemctl failed. Attempting manual Redis launch..."
nohup redis-server > redis.log 2>&1 &
sleep 2
fi
fi

if redis-cli ping > /dev/null 2>&1; then
echo "✅ Redis is active."
else
echo "❌ Redis is not running. Try manually with:"
echo "   sudo systemctl start redis"
echo "   OR run: redis-server"
fi

# Ensure scripts are executable

chmod +x start\_workers.sh setup\_system.sh

# Final instructions

echo "\n🎯 Setup finished successfully!"
echo "Next steps:"
echo "1️⃣  Edit .env and insert your OpenAI key"
echo "2️⃣  Start workers using: ./start\_workers.sh"
echo "3️⃣  In another terminal, launch API: python main.py"
echo "4️⃣  Navigate to: [http://localhost:8000](http://localhost:8000)"
echo "5️⃣  Flower dashboard: [http://localhost:5555](http://localhost:5555)"
echo "\n🐳 Docker setup: docker-compose up -d"
echo "\n🚀 You're ready to analyze blood test reports!"
