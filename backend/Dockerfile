# 1. Use a lightweight Python base image
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies (if any)
RUN apt-get update && apt-get install -y \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# 4. Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your backend code
COPY . .

# 6. Create directories for SQLite data and logs, and make them writable
RUN mkdir -p /app/data /app/logs && \
    chmod 755 /app/data /app/logs

# 7. Expose the port your FastAPI app listens on
EXPOSE 8000

# 8. Default command: start Uvicorn with live reload in dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
