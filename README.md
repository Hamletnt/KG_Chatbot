"# Graph RAG Chatbot

A web-based chatbot powered by Graph Retrieval-Augmented Generation (RAG) using Neo4j and Azure OpenAI.

## Features

- **Graph RAG**: Combines knowledge graphs with vector similarity search
- **Web Interface**: Clean, responsive chat interface
- **Docker Support**: Easy deployment with Docker Compose
- **FastAPI Backend**: Modern, fast API framework
- **Real-time Chat**: Interactive chat experience

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   FastAPI App   │◄──►│     Neo4j DB    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Azure OpenAI   │
                       └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for development)
- Azure OpenAI API access

### 1. Environment Setup

Copy the environment template and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_CHAT_DEPLOYMENT=your-chat-deployment
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your-embeddings-deployment
AZURE_OPENAI_API_VERSION=2024-02-01

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=test1234
```

### 2. Start Services

```bash
# Start Neo4j and the web application
docker-compose up -d
```

### 3. Initialize Data

```bash
# Activate virtual environment
.\venv310\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize the graph database
python init_data.py
```

### 4. Access the Application

Open your browser and navigate to: http://localhost:8000

## Development Setup

### Using Virtual Environment

```bash
# Activate virtual environment
.\venv310\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Start Neo4j only
docker-compose up neo4j -d

# Initialize data
python init_data.py

# Run the application
python run.py
```

### Project Structure

```
chatbot-project/
├── src/                    # Application source code
│   ├── api/               # FastAPI routes
│   ├── config/            # Configuration management
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── main.py           # Application entry point
├── static/                # Static files (CSS, JS)
├── templates/             # HTML templates
├── data/                 # Neo4j data directory
├── neo4j/               # Neo4j Docker configuration
├── venv310/             # Python virtual environment
├── docker-compose.yaml  # Docker services configuration
├── Dockerfile          # Web app container
├── requirements.txt    # Python dependencies
├── init_data.py       # Database initialization script
└── run.py            # Local development runner
```

## API Endpoints

### Chat API

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Who is Nonna Lucia?",
  "conversation_id": "optional-uuid"
}
```

Response:
```json
{
  "response": "Nonna Lucia is...",
  "conversation_id": "uuid",
  "sources": null
}
```

### Health Check

```http
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "azure_openai_configured": true
}
```

## How It Works

1. **Document Processing**: Text documents are split into chunks and converted to graph documents
2. **Graph Creation**: Entities and relationships are extracted and stored in Neo4j
3. **Vector Indexing**: Document embeddings are created and stored for similarity search
4. **Query Processing**: User queries trigger both graph traversal and vector similarity search
5. **Response Generation**: Retrieved context is used to generate responses via Azure OpenAI

## Customization

### Adding New Documents

1. Place your text files in the project directory
2. Update `init_data.py` to load your documents
3. Run the initialization script

### Modifying the UI

- Edit `templates/index.html` for HTML structure
- Modify `static/style.css` for styling
- Update `static/script.js` for JavaScript functionality

### Extending the API

- Add new routes in `src/api/`
- Create new services in `src/services/`
- Define new models in `src/models/`

## Troubleshooting

### Common Issues

1. **Neo4j Connection Error**
   - Ensure Neo4j is running: `docker-compose ps`
   - Check Neo4j logs: `docker-compose logs neo4j`

2. **Azure OpenAI Authentication Error**
   - Verify your API key and endpoint in `.env`
   - Check deployment names match your Azure configuration

3. **Empty Responses**
   - Ensure data has been initialized: `python init_data.py`
   - Check if fulltext index exists in Neo4j browser

### Logs

```bash
# View application logs
docker-compose logs chatbot-web

# View Neo4j logs
docker-compose logs neo4j
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request" 
