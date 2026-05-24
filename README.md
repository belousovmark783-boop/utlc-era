# UTLC ERA v2.1

## Развёртывание у себя

Проект использует **PostgreSQL 16+**.
### 1. Установи PostgreSQL
- Windows: https://www.postgresql.org/download/windows/
- macOS: `brew install postgresql@16 && brew services start postgresql@16`
- Linux: `sudo apt install postgresql-16`

### 2. Создай базу
```bash
# Подключиться под суперюзером и создать БД
psql -U postgres -c "CREATE DATABASE utlc_era;"
```

### 3. Настрой backend/.env
```bash
cp backend/.env.example backend/.env
```
Открой `backend/.env` и заполни параметры подключения:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=utlc_era
DB_USER=postgres
DB_PASSWORD=<твой пароль postgres>
```

### 4. Запусти backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
При первом запуске таблицы и миграции создадутся автоматически.

### 5. Запусти frontend
```bash
cd frontend
npm install
npm run dev
```
Открой http://localhost:5173.

---

## Быстрый старт (Docker)

```bash
# 1. Скопировать конфиг
cp backend/.env.example backend/.env

# 2. Заполнить .env (CORS_ORIGINS, API_KEY и др.)
nano backend/.env

# 3. Запустить
docker compose up -d

# Бэкенд:  http://localhost:8000
# API docs: http://localhost:8000/docs
# Фронт:   http://localhost:5173
```

## Без Docker

```bash
# Бэкенд
cd backend
pip install -r requirements.txt
cp .env.example .env  # отредактировать
uvicorn main:app --host 0.0.0.0 --port 8000

# Фронтенд
cd frontend
npm install
npm run dev
```

## Переменные окружения (backend/.env)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `HOST` | `0.0.0.0` | Адрес прослушивания |
| `PORT` | `8000` | Порт |
| `DEBUG` | `false` | Режим отладки (не включать в prod) |
| `DB_PATH` | `database.db` | Путь к SQLite-файлу |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Разрешённые origins (через запятую) |
| `API_KEY` | _(пусто)_ | Если задан — требуется заголовок `X-API-Key` |
| `FBX_API_KEY` | _(пусто)_ | Freightos FBX (морские ставки, live) |
| `ERAI_API_KEY` | _(пусто)_ | ERAI Index UTLC ERA (ж/д ставки, live) |

## Эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/health` | Статус сервиса и БД |
| POST | `/api/simple-analyze` | Анализ маршрутов (основной) |
| POST | `/api/enrich` | Параметры маршрута без расчёта TCO |
| GET | `/api/indicative-rate` | Индикативная ставка фрахта |
| GET | `/api/history` | История анализов |
| GET | `/docs` | Swagger UI |

## Что было исправлено (v2.1 vs v2.0)

- ✅ Ставка страховки: дефолт 2% → 0.2% (соответствует ICC/Lloyd's)
- ✅ Двойной счёт `intransit_cap`: вычитается авансовый платёж
- ✅ TEU: ставка фрахта умножается на количество контейнеров
- ✅ `transit_days`: учитывает реальное расстояние (`max(days_base, days_dist)`)
- ✅ `config.py`: читает переменные из `.env` / окружения
- ✅ `init_db()`: вызывается через `lifespan` (работает с uvicorn/gunicorn)
- ✅ `carrier_rate_usd=0`: разрешено — автоматически берётся индикативная ставка
- ✅ CORS: настраивается через `CORS_ORIGINS` в `.env`
- ✅ API-ключ: опциональная защита через `X-API-Key`
- ✅ Health check: проверяет доступность БД
- ✅ Добавлены `Dockerfile` и `docker-compose.yml`
