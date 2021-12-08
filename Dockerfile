FROM python:3.10.1-slim-buster

COPY . /app
WORKDIR /app
RUN python3 -m pip install -r requirements.txt
ENTRYPOINT ["python", "crawler.py"]
