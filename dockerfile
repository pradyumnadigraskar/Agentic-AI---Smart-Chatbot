# ===============================
# Stage 1: Base image
# ===============================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# Stage 2: Install Python deps
# ===============================
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ===============================
# Stage 3: Copy project files
# ===============================
COPY . .

# ===============================
# Stage 4: Expose port & run
# ===============================
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "Rag/app/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
