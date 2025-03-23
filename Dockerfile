FROM python:3.10-slim

# Install git and curl (needed for Poetry installation)
RUN apt-get update && \
    apt-get install -y git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/

# Set up working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock (if exists)
COPY pyproject.toml ./
COPY poetry.lock* ./

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy application code
COPY . .

# Create volume mount point for git repositories
VOLUME /git

# Set working directory to mounted git repo
WORKDIR /git

# Set entrypoint
ENTRYPOINT ["unfck"]
