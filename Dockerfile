# Use Alpine Linux for a minimal footprint
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Upgrade system packages to patch OS-level CVEs
RUN apk update && apk upgrade --no-cache

# Copy and install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

LABEL version="0.1" \
      description="Containerized Generate: License Returner"

# Execute code directly using the system Python
ENTRYPOINT [ "python3", "/app/license_returner/return_license.py" ]