FROM python:3.11-slim
WORKDIR /app
COPY backup_data.py .
RUN pip install --no-cache-dir psutil
CMD ["python", "backup_data.py"]
