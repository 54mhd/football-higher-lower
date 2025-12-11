# Use an official Python runtime
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Run your FastAPI application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
