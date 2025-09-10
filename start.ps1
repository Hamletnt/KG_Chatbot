# Graph RAG Chatbot Startup Script

Write-Host "Starting Graph RAG Chatbot..." -ForegroundColor Green
Write-Host ""

# Step 1: Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv310\Scripts\Activate.ps1"

# Step 2: Start Neo4j
Write-Host ""
Write-Host "[2/4] Starting Neo4j database..." -ForegroundColor Yellow
docker-compose up neo4j -d

# Step 3: Wait for Neo4j
Write-Host ""
Write-Host "[3/4] Waiting for Neo4j to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Step 4: Start the application
Write-Host ""
Write-Host "[4/4] Starting the web application..." -ForegroundColor Yellow
Write-Host "Open your browser and navigate to: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

python run.py
