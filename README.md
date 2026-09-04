# Каталог товаров — Shop API (FastAPI)

Асинхронный REST API каталога товаров на FastAPI с поддержкой категорий и продуктов.

## Эндпоинты API

### Категории
- `GET /api/categories` — список категорий (с пагинацией: page, per_page)
- `POST /api/categories` — создание категории
- `GET /api/categories/{id}` — детали категории
- `PUT /api/categories/{id}` — обновление категории
- `DELETE /api/categories/{id}` — удаление категории

### Товары
- `GET /api/products` — список товаров с фильтрацией и пагинацией
  - Параметры: min_price, max_price, category_id, search, is_active, page, per_page
- `POST /api/products` — создание товара
- `GET /api/products/{id}` — детали товара
- `PUT /api/products/{id}` — обновление товара
- `DELETE /api/products/{id}` — удаление товара

## Установка

1. Создать виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Создать базу данных PostgreSQL:
```sql
CREATE DATABASE shop_api;
```

4. Скопировать `.env.example` в `.env` и при необходимости изменить параметры подключения:
```bash
copy .env.example .env
```

## Запуск

```bash
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу http://127.0.0.1:8000

Интерактивная документация Swagger UI: http://127.0.0.1:8000/docs

Альтернативная документация ReDoc: http://127.0.0.1:8000/redoc

## Запуск тестов

```bash
pytest
```

Для вывода подробного вывода:
```bash
pytest -v
```
