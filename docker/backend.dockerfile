FROM python:3.11.7

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev

WORKDIR /src

COPY requirements.txt /src/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /src

# удалить --reload из прод запуска, добавить в дев
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]