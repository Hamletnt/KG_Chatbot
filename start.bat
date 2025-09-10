@echo off
echo Starting Graph RAG Chatbot...

echo.
echo [1/4] Activating virtual environment...
call .\venv310\Scripts\activate.bat

echo.
echo [2/4] Starting Neo4j database...
docker-compose up neo4j -d

echo.
echo [3/4] Waiting for Neo4j to be ready...
timeout /t 10 /nobreak > nul

echo.
echo [4/4] Starting the web application...
python run.py

pause
