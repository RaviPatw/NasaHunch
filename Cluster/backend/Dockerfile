FROM python:3.11-slim

WORKDIR /app

# Install build tools and PostgreSQL client headers
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Force source install to compile for ARM
RUN pip install --no-cache-dir --no-binary=:all: -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
