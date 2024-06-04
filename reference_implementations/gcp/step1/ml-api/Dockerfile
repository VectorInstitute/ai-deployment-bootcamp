FROM python:3.9.19-slim-bookworm

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["fastapi", "run", "main.py", "--port", "8080"]
