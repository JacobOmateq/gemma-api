# gemma-api

A FastAPI service that uses Ollama to run the Gemma model for extracting structured information from text. The service provides a REST API endpoint that accepts text input and returns JSON-formatted extracted information.

## Features

- REST API endpoint for text analysis
- Configurable system prompts
- Docker containerization
- Automatic model loading
- Health check endpoint
- Retry mechanism for reliability
- Customizable JSON extraction

## Prerequisites

- Docker and Docker Compose
- `jq` command-line tool (for script functionality)

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

### Extract Information

```bash
curl --location 'http://localhost:8000/extract_department' \
--header 'Content-Type: application/json' \
--data '{
    "title": "Your text here",
    "system_prompt": "Optional custom prompt"
}'
```

#### Response Format
```json
{
    "content": {
        // Extracted information in JSON format
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