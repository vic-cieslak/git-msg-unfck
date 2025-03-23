FROM python:3.10-slim

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create volume mount point for git repositories
VOLUME /git

# Set working directory to mounted git repo
WORKDIR /git

# Set entrypoint
ENTRYPOINT ["unfck"]
