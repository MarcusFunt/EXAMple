#!/bin/bash

set -e

echo "Starting AI Notes Server Installation..."

# Check dependencies
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker and try again."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install it and try again."
    exit 1
fi

# Run hardware detection
echo "Detecting hardware..."
chmod +x scripts/detect_hardware.sh
./scripts/detect_hardware.sh

# Load selected model from .env
if [ -f .env ]; then
    export $(grep SELECTED_MODEL .env | xargs)
else
    echo "Error: .env file was not generated."
    exit 1
fi

echo "Pulling and starting containers..."
docker compose up -d

echo "Waiting for Ollama to be ready..."
until docker exec ollama ollama list &> /dev/null; do
    sleep 2
done

echo "Pulling model: $SELECTED_MODEL..."
docker exec ollama ollama pull "$SELECTED_MODEL"

echo "------------------------------------------------"
echo "Installation Complete!"
echo "AI Notes Server is running."
echo "Access the web interface at: http://localhost:8501"
echo "Selected Model: $SELECTED_MODEL"
echo "------------------------------------------------"
