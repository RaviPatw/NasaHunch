FROM python:3.11-slim
WORKDIR /app
COPY maintenance_report.py .
RUN pip install --no-cache-dir psutil prometheus_client
CMD ["python", "maintenance_report.py"]
