## Troubleshooting

This guide covers common issues when running the app locally or in Docker.

---

## Containers Won't Start

1. Check if port `8501` is already in use:

```bash
lsof -i :8501
```

2. Stop any existing Streamlit processes.  
3. Check Docker logs:

```bash
docker logs llm-judge-app
```

If using Docker Compose:

```bash
docker-compose logs
```

---

## Can't Connect to Ollama

- Verify Ollama is running:

```bash
ollama list
```

- Check `OLLAMA_HOST` environment variable.  
- For Docker, ensure Ollama is accessible from the container:
  - macOS/Windows: `host.docker.internal:11434` usually works
  - Linux: consider `--network host` or custom Docker networking

Check from inside the container:

```bash
docker exec llm-judge-app env | grep OLLAMA_HOST
```

---

## Stop Button Appears Not to Work

- The stop button **prevents results from being shown or saved**, but the underlying Ollama request may still complete.  
- If the UI feels stuck, refresh the page; it auto-polls every few seconds.  

---

## Database Not Found

- The database is created automatically on first save.  
- Check that:
  - `./data/` directory exists (for Docker)
  - Project root is writable (local)  

Commands to inspect:

```bash
ls -lh ./data/
sqlite3 ./data/llm_judge.db ".tables"
```

---

## Docker Quick Checks

If you run into Docker issues:

```bash
# Check if port 8501 is in use
lsof -i :8501

# Remove existing container if needed
docker rm -f llm-judge-app

# Rebuild and restart
docker-compose build
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

