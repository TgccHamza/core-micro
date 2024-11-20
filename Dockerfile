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

# Set working directory and change ownership
WORKDIR /app
RUN mkdir /app/tmp
# Install system dependencies and cleanup in a single layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libc6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pip-tools

# Copy and install requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
#

## Change ownership of the application directory
#RUN chown -R appuser:appuser /app
#
## Switch to non-root user
#USER appuser
#
## Create and use a virtual environment
#RUN python -m venv /app/venv
#ENV PATH="/app/venv/bin:$PATH"

# Expose the port that FastAPI runs on
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use a non-root user to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0",  "--port", "8000", "--no-access-log", "--reload"]