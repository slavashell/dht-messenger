FROM python:3.8-slim

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /
RUN pip install -r requirements.txt

RUN mkdir /app
COPY messenger /app
WORKDIR /app

EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
