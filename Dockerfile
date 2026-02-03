FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
# Root app.py has been deleted - all functionality moved to frontend/app.py
COPY api_client.py .
# Copy frontend and backend directories
COPY frontend frontend/
COPY backend backend/
# Copy modular package
COPY core core/

# Copy .streamlit config directory if it exists
COPY .streamlit .streamlit/

# Create directory for database with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV OLLAMA_HOST=http://host.docker.internal:11434
ENV DB_PATH=/app/data/llm_judge.db

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit from frontend/app.py
# Root app.py has been deleted - all functionality migrated to frontend/app.py
# Evaluation functions accessed via backend/services/evaluation_functions.py compatibility layer
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

