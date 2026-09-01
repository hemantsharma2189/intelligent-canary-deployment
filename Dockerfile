FROM python:3.12-slim

LABEL maintainer="Hemant Sharma"
LABEL description="Kubernetes canary deployment demo application"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system canary \
    && useradd --system --gid canary canary

COPY app/app.py .

RUN chown -R canary:canary /app

USER canary

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
