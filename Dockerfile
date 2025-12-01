FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential gcc libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt ./server_requirements.txt
COPY server/requirements-dev.txt ./server_requirements_dev.txt
RUN python -m pip install --upgrade pip
RUN pip install -r ./server_requirements.txt || true
RUN pip install -r ./server_requirements_dev.txt || true

COPY . /app

EXPOSE 5000
CMD ["gunicorn", "server.app:app", "-b", "0.0.0.0:5000", "--workers", "2"]
