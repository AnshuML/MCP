FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Production settings
ENV MCP_TRANSPORT=streamable-http
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "src.main"]
