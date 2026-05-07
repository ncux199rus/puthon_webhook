FROM python:3.12-slim

WORKDIR /app

# системные зависимости (по минимуму)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# сначала зависимости (лучше кэш)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# затем код
COPY . /app

# uvicorn слушает внутри контейнера
EXPOSE 8007

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
CMD ['/app/dist']