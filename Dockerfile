# Use a specific version of Python slim-bullseye for better security
FROM python:3.11-slim-bullseye

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Create necessary directories and files with proper permissions
RUN mkdir -p /app/tmp_uploads /app/tmp \
&& touch /app/uvicorn_logs.log \
&& chown -R appuser:appuser /app \
&& chmod 755 /app \
&& chmod -R 755 /app/tmp_uploads /app/tmp \
&& chmod 644 /app/uvicorn_logs.log

# Install system dependencies and cleanup in a single layer
RUN apt-get update \
&& apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libc6-dev \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* \
&& pip install --no-cache-dir pip-tools

# Copy requirements and install dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and set ownership
COPY --chown=appuser:appuser . .

# Create and use a virtual environment
RUN python -m venv /app/venv \
&& chown -R appuser:appuser /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Expose the port that FastAPI runs on
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]