# REST-API для операций над изображениями на FastAPI (pillow)

### Описание

Сервис для конвертации изображений.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
   bash
   pip install -r requirements.txt
3. poetry install
4. pre-commit install
5. pre-commit run --all-files

## Запуск БД

COMPOSE_FILE=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""

## Команды для docker compose

docker compose up --build -d
docker compose down -v
docker compose exec имя*контейнера psql -U имя*пользователя имя_бд

## Запуск тестов

pytest
