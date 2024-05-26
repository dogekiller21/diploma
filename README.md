# Дипломчик

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## Dev

```bash
pip install -r requirements-dev.txt
```

```bash
pre-commit install
```

### Перед коммитом 
```bash
pre-commit run --all-files
```
## Запуск

### Используя Docker
```bash
docker-compose -f docker-compose-dev.yaml up -d
```

### Используя Make
```bash
make start-dev
```

Приложение доступно на `localhost`

Документацию к api можно прочитать на `localhost/docs`


# TODO

При маппинге nginx директорий он не хочет стартовать