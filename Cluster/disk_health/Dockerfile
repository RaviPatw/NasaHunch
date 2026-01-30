FROM python:3.11-slim

WORKDIR /app

# Install build tools needed to compile psutil on ARM64
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY maintenance_report.py .

RUN pip install --no-cache-dir psutil prometheus_client

CMD ["python", "maintenance_report.py"]
