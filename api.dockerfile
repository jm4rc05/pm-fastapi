FROM python:3.11-slim AS apibase

EXPOSE 8000

WORKDIR /var/task

COPY requirements.txt /var/task

RUN pip install --no-cache-dir --upgrade -r /var/task/requirements.txt

COPY app /var/task
COPY app/.env /var/task

CMD ["python", "main.py"]
