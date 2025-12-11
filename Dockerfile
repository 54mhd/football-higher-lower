FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project
COPY ./app ./app
COPY ./main.py .
COPY ./index.html .
COPY ./game.html .
COPY ./trivia.html .

# Expose FastAPI port
EXPOSE 8000

# Run using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
