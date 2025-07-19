FROM python:3.11.6
WORKDIR /app

COPY . /app

RUN pip cache purge
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt --no-cache-dir