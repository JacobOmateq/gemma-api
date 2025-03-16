# gemma-api

A FastAPI service that provides a REST API for interacting with the Gemma language model through Ollama. The service is designed to be flexible and can be used for various natural language processing tasks by customizing the system prompt.

## Features

- Generic REST API for LLM interaction
- Configurable system prompts for different use cases
- Docker containerization
- Automatic model loading
- Health check endpoint
- Retry mechanism for reliability
- JSON response formatting

## Prerequisites

- Docker and Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/JacobOmateq/gemma-api
cd gemma-api
```

2. Start the service:
```bash
./start.sh
```

Or for a complete rebuild:
```bash
./rebuild.sh
```

## Configuration

### System Prompt

The default system prompt is configured in `llm_settings.json`. You can customize it for your specific use case:

```json
{
    "model": "gemma3:1b",
    "system_prompt": "Your custom prompt here..."
}
```

## API Endpoints

### Generate Response

```bash
curl --location 'http://localhost:8000/generate' \
--header 'Content-Type: application/json' \
--data '{
    "text": "Your input text here",
    "system_prompt": "Optional custom prompt to define the task"
}'
```

Example use cases:
1. Information Extraction:
```json
{
    "text": "Meeting with John tomorrow at 2 PM",
    "system_prompt": "Extract event details and return them as JSON with fields: type, person, time"
}
```

2. Text Classification:
```json
{
    "text": "I love this product, it works great!",
    "system_prompt": "Analyze the sentiment of this text and return JSON with fields: sentiment, confidence"
}
```

3. Structured Data Generation:
```json
{
    "text": "Create a character profile for a fantasy story",
    "system_prompt": "Generate a character profile and return as JSON with fields: name, race, class, abilities, background"
}
```

#### Response Format
```json
{
    "content": {
        // JSON formatted response
        // Structure depends on the system prompt
    }
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
    "status": "healthy",
    "ollama": "connected"
}
```

## Development

### Project Structure

```
gemma-api/
├── main.py           # FastAPI application
├── llm_settings.json # Model and prompt configuration
├── start.sh         # Service startup script
├── rebuild.sh       # Rebuild script for development
├── Dockerfile       # Container definition
└── docker-compose.yml
```

### Scripts

- `start.sh`: Initial startup of the service
- `rebuild.sh`: Complete rebuild of the containers (useful during development)

### Rebuilding the Service

During development, use the rebuild script to apply changes:

```bash
./rebuild.sh
```

This will:
1. Stop existing containers
2. Rebuild images from scratch
3. Start the services
4. Pull the required Ollama model

## Troubleshooting

### Logs

View service logs:
```bash
docker-compose logs -f
```

View specific service logs:
```bash
docker-compose logs -f api  # For the API service
docker-compose logs -f ollama  # For the Ollama service
```

### Common Issues

1. If the service returns `null` responses, check:
   - Ollama model availability
   - JSON parsing in the response
   - System prompt formatting

2. If the service is unhealthy:
   - Verify Ollama container is running
   - Check resource availability
   - Review API logs

## License

MIT