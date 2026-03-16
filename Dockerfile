FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and external APIs config (Phase 3)
COPY src/ ./src/
COPY config/ ./config/
COPY pyproject.toml .

# Production settings
ENV MCP_TRANSPORT=streamable-http
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "src.main"]
