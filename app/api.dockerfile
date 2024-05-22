FROM python:3.11-slim AS apibase

EXPOSE 8000

WORKDIR /var/task

COPY app /var/task
COPY app/.env /var/task

RUN pip install --no-cache-dir --upgrade -r /var/task/requirements.txt

CMD ["uvicorn", "main:api", "--port", "8000"]
