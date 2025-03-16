#!/bin/bash

echo "Stopping containers..."
docker-compose down

echo "Building new images..."
docker-compose build --no-cache

echo "Starting containers..."
docker-compose up -d

# Extract model name from llm_settings.json using jq
MODEL=$(jq -r '.model' llm_settings.json)

echo "Pulling Ollama model: $MODEL"
docker-compose exec -T ollama ollama pull $MODEL

echo "Rebuild complete! Services are starting..."
echo "You can check the logs with: docker-compose logs -f" 