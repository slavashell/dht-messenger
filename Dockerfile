FROM python:3.8-slim

COPY requirements.txt /
RUN pip install -r requirements.txt

RUN mkdir /app
COPY messenger /app
WORKDIR /app

EXPOSE 8000
# CMD ["sleep", "9999"]
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
