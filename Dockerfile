FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN pip install -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["ai-voice-scraper"]
