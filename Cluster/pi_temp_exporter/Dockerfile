FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pi_temp_exporter.py .

EXPOSE 9300

CMD ["python", "pi_temp_exporter.py"]
