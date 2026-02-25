FROM python:3.11-slim

WORKDIR /app

# Install build tools and Python headers needed for ARM compilation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    smartmontools \
    && rm -rf /var/lib/apt/lists/*

COPY maintenance_report.py .

RUN pip install --no-cache-dir psutil prometheus_client

CMD ["python", "maintenance_report.py"]
