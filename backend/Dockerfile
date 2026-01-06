FROM python:3.11-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
# Copy utility files first to cache dependencies
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Sync the project (installs the project itself if configured) and ensures venv is ready
RUN uv sync --frozen --no-dev

# Place the virtual environment in the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
