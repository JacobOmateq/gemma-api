#!/bin/bash

# Extract model name from llm_settings.json using jq
MODEL=$(jq -r '.model' llm_settings.json)

# Start the containers
docker-compose up -d

# Pull the specific model
docker-compose exec ollama ollama pull $MODEL

echo "Started containers and pulled model: $MODEL"