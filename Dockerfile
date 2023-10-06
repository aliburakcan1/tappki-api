FROM python:3.11-slim
ENV APP_ENV=dev
RUN mkdir /app
WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt

RUN apt update && apt install curl && curl -L https://install.meilisearch.com

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]