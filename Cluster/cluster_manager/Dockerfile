FROM python:3.11-slim
WORKDIR /app
COPY auto_mantain.py .
RUN pip install --no-cache-dir psutil
CMD ["python", "auto_mantain.py"]
