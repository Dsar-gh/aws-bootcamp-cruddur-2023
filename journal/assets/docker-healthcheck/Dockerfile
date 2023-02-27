FROM python:3.6-alpine

COPY . /docker-healthcheck

WORKDIR /docker-healthcheck

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
