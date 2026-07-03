FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/backend

WORKDIR /app/backend

RUN addgroup --system app && adduser --system --ingroup app app

COPY backend/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY --chown=app:app backend /app/backend
COPY --chown=app:app gita_book.pdf krishna_ji.jpeg /app/
RUN mkdir -p /data/uploads && chown -R app:app /data/uploads

USER app
EXPOSE 8000

CMD ["sh", "entrypoint.sh", "api"]
