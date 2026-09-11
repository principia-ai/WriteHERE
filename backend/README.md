# WriteHERE Backend Server

This is the backend server for the WriteHERE application, which interfaces with the Heterogeneous Recursive Planning engine to generate stories and reports.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the main project dependencies installed:
```bash
pip install -v -e .
```

3. Run the server:
```bash
python server.py
```

The server will start on http://localhost:5001.

## API Endpoints

### Generate Story
```
POST /api/generate-story
```
Request body:
```json
{
  "prompt": "Write a story about...",
  "model": "gpt-4o",
  "apiKeys": {
    "openai": "sk-...",
    "claude": "sk-ant-..."
  }
}
```

Use local Ollama models with the `ollama/` prefix, for example `ollama/qwen2.5:7b`. Local models do not require cloud API keys, but Ollama must already be running locally.

### Generate Report
```
POST /api/generate-report
```
Request body:
```json
{
  "prompt": "Write a report about...",
  "model": "claude-3-5-sonnet-20241022",
  "enableSearch": true,
  "searchEngine": "google",
  "apiKeys": {
    "openai": "sk-...",
    "claude": "sk-ant-...",
    "serpapi": "..."
  }
}
```

### Get Generation Status
```
GET /api/status/{taskId}
```

### Get Generation Result
```
GET /api/result/{taskId}
```

### List Models
```
GET /api/models
```
Returns built-in online model suggestions plus local Ollama models discovered from `OLLAMA_MODELS_DIR` or `~/.ollama/models`.

## Integration with Frontend

The frontend makes API calls to these endpoints to trigger generation tasks and monitor their progress. The API keys provided by users in the frontend are passed to the backend server, which uses them to authenticate with the respective services.

Note that API keys are never stored on the server beyond the duration of the task execution.
