#!/bin/bash

echo "=== Liminal Horror Reel Generator Setup ==="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# 2. Virtual Environment (optional but good practice)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate venv
source venv/bin/activate

# 4. Install Dependencies
echo "Installing/Updating dependencies..."
pip install -r requirements.txt

# 5. Check .env
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "OPENAI_API_KEY=your_key_here" > .env
    echo "MOCK_GENERATION=true" >> .env
    echo "Please edit .env with your real API key."
fi

# 6. Run Server?
read -p "Do you want to start the Automation Server (Make.com webhook)? (y/n) " start_server

if [[ $start_server =~ ^[Yy]$ ]]; then
    echo "Starting Server on port 5001..."
    echo "Use 'ngrok http 5001' to expose this to the internet."
    python3 server.py
else
    # 7. Run Generator?
    read -p "Do you want to generate a single video now? (y/n) " start_gen
    if [[ $start_gen =~ ^[Yy]$ ]]; then
        python3 main.py
    fi
fi

echo "Done."
