#!/bin/bash
# Script to check if database exists in Docker container

echo "Checking database in Docker container..."
echo ""

# Check if container is running
if docker ps | grep -q llm-judge-app; then
    echo "✅ Container is running"
    echo ""
    
    # Check if database file exists in container
    echo "Checking for database file in container..."
    if docker exec llm-judge-app ls -lh /app/data/llm_judge.db 2>/dev/null; then
        echo ""
        echo "✅ Database file exists in container at /app/data/llm_judge.db"
        echo ""
        echo "Database size:"
        docker exec llm-judge-app ls -lh /app/data/llm_judge.db
    else
        echo "⚠️  Database file not found in container yet."
        echo "   It will be created when you save your first judgment."
    fi
    
    echo ""
    echo "Checking host machine data directory..."
    if [ -f "./data/llm_judge.db" ]; then
        echo "✅ Database file exists on host at ./data/llm_judge.db"
        ls -lh ./data/llm_judge.db
    else
        echo "⚠️  Database file not found on host yet."
        echo "   It will be created when you save your first judgment."
    fi
    
    echo ""
    echo "To view database contents, run:"
    echo "  docker exec llm-judge-app sqlite3 /app/data/llm_judge.db '.tables'"
    echo ""
    echo "To check database from host:"
    echo "  sqlite3 ./data/llm_judge.db '.tables'"
    
else
    echo "❌ Container is not running"
    echo "   Start it with: docker-compose up -d"
fi

