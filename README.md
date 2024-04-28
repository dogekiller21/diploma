# Дипломчик

## Запуск

### MacOS
*homebrew должен быть установлен*

#### 1. Установка python

```bash
brew install python
```

#### 2. Установка neo4j
```bash
brew intall neo4j
```

#### 3. Запуск neo4j
```bash
neo4j start
```

#### 4. Копирование файла .env
```bash
cp .env.example .env
```

#### 5. Установка зависимостей requirements

```bash
pip install -r requirements.txt
```

#### 6. Запуск приложения

```bash
uvicorn app.main:app
```
или
```bash
./run_app.sh
```

TODO: docker