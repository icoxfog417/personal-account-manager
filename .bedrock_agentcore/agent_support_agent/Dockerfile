FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

# Install git for GitPython as root
USER root
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# All environment variables in one layer
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-east-1 \
    AWS_DEFAULT_REGION=us-east-1

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN uv pip install -r requirements.txt
RUN uv pip install aws-opentelemetry-distro>=0.10.1

# Copy entire project
# Cache bust: 2025-10-27-16:50-txt-files
COPY . .

# Create non-root user and change ownership
RUN useradd -m -u 1000 bedrock_agentcore && \
    chown -R bedrock_agentcore:bedrock_agentcore /app

# Switch to non-root user
USER bedrock_agentcore

# AgentCore Runtime expects port 8080
EXPOSE 8080

CMD ["opentelemetry-instrument", "python", "__main__.py"]
