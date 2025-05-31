# Use a lightweight Python image
FROM python:3.11-slim

# Install ffmpeg, git, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app code into container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (default for gunicorn)
EXPOSE 8000

# Run using gunicorn
CMD ["gunicorn", "ballpoint_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
