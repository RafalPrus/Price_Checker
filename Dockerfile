FROM python:3.10-slim

# Set workdir in container
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATA_FILE /data/tracked_links.json

EXPOSE 5000

CMD ["python", "app_flask.py"]
