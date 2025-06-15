#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting Docker installation and build process..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Docker not found. Attempting to install Docker for macOS..."

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "🔧 Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi

    # Install Docker using Homebrew
    brew install --cask docker

    echo "📦 Docker installed. Please open Docker Desktop manually to complete setup if this is the first time."
    exit 1  # Exit so user can manually start Docker Desktop
else
    echo "✅ Docker is already installed."
fi

# Wait for Docker daemon to be ready
while ! docker info > /dev/null 2>&1; do
    echo "⏳ Waiting for Docker to start..."
    sleep 2
done

echo "🔧 Building Docker image from deploy/image/Dockerfile..."

docker build -f deploy/image/Dockerfile -t bookstore:latest .

echo "💾 Saving Docker image to tar archive..."
docker save bookstore:latest -o django_app.tar

echo "🎉 Docker build and save completed successfully!"
