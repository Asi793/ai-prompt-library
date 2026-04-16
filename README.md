# AI Prompt Library

A full-stack web application for storing and managing AI image generation prompts.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Angular 16 |
| Backend | Python / Django 4.2 |
| Database | PostgreSQL 14 |
| Cache / Counters | Redis 7 |
| Containerization | Docker + Docker Compose |

## Features

- Browse all saved prompts with complexity badges
- View full prompt details with a live Redis-backed view counter
- Add new prompts with reactive form validation (frontend + backend)
- Color-coded complexity levels: green (1–3), orange (4–7), red (8–10)

## Project Structure

```
ai-prompt-library/
├── backend/
│   ├── config/           # Django project settings & URLs
│   ├── prompts/          # App: model, views, URLs, admin
│   ├── manage.py
│   ├── requirements.txt
│   ├── entrypoint.sh     # Waits for DB, runs migrations, starts server
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── components/
│   │       │   ├── prompt-list/
│   │       │   ├── prompt-detail/
│   │       │   └── add-prompt/
│   │       └── services/prompt.service.ts
│   ├── nginx.conf        # Serves Angular + proxies /api/ to backend
│   └── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

## Quick Start (Docker)

**Prerequisites:** Docker Desktop installed and running. Download from https://www.docker.com/products/docker-desktop

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-prompt-library

# 2. Build and start all 4 containers (frontend, backend, postgres, redis)
docker-compose up --build
```

Wait until you see this in the terminal:
```
backend-1  | Watching for file changes with StatReloader
```

```bash
# 3. First time only — open a NEW terminal and run migrations
docker-compose exec backend python manage.py makemigrations prompts
docker-compose exec backend python manage.py migrate
```

```bash
# 4. Open the app
#    Frontend → http://localhost:4200
#    Backend API → http://localhost:8000/api/prompts/
#    Django Admin → http://localhost:8000/admin/
```

> After the first run, migrations apply automatically on every subsequent `docker-compose up`.

### Stopping the app
```bash
docker-compose down        # stops containers, data is preserved
docker-compose down -v     # ⚠️ WARNING: also deletes the database volume (data lost)
```

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables (or create a .env and export manually)
export POSTGRES_DB=library_db
export POSTGRES_USER=library_user
export POSTGRES_PASSWORD=library_password
export POSTGRES_HOST=localhost
export REDIS_HOST=localhost

python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm start          # proxies /api/ to http://localhost:8000
# Open http://localhost:4200
```

## API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/api/prompts/` | List all prompts |
| POST | `/api/prompts/` | Create a new prompt |
| GET | `/api/prompts/<id>/` | Get one prompt (increments Redis view counter) |

### POST `/api/prompts/` — Request body

```json
{
  "title": "Cyberpunk cityscape at dusk",
  "content": "A highly detailed cyberpunk city at dusk, neon lights, rain-slicked streets, flying cars",
  "complexity": 7
}
```

### Validation rules

- `title` — minimum 3 characters
- `content` — minimum 20 characters
- `complexity` — integer between 1 and 10

## Architecture Notes

```
Browser (Angular at :4200)
        |
        | HTTP requests
        ↓
    nginx (port 80 inside container)
        |
        | proxies /api/* to Django
        ↓
Django Backend (:8000)
        |               |
        ↓               ↓
  PostgreSQL           Redis
 (stores prompts)   (view counts)
```

- **View counter:** Redis `INCR prompt:<id>:views` is called on every `GET /api/prompts/<id>/` request. PostgreSQL stores the canonical prompt data; Redis is the source of truth for view counts only.
- **CORS:** `django-cors-headers` allows Angular dev server (`localhost:4200`) to talk to Django directly. In Docker, nginx routes everything through port 4200 so no CORS headers are needed.
- **Migrations in Docker:** `entrypoint.sh` polls for PostgreSQL readiness before running `python manage.py migrate`, preventing startup race conditions.
- **Angular routing:** HTML5 pushState routing is enabled. nginx is configured with `try_files $uri $uri/ /index.html` so deep links work after a page refresh.
- **nginx DNS resolver:** Docker's internal DNS (`127.0.0.11`) is used so nginx re-resolves the `backend` hostname at request time instead of caching it at startup.

---

## Assumptions and Trade-offs

- **Plain Django views instead of DRF:** The assignment required standard Django views returning JSON. This keeps the backend lightweight but means manual JSON parsing and response building instead of using serializers.
- **Redis view counts are not persisted to PostgreSQL:** View counts live only in Redis. If the Redis container is removed with `docker-compose down -v`, counts reset to zero. This is intentional — Redis is used as a fast in-memory counter, not a permanent store.
- **No authentication:** Prompts are publicly readable and writable by anyone. Adding authentication was listed as a bonus feature and is not included in the base implementation.
- **SQLite not used:** PostgreSQL was chosen as required, even for local development, to match production behaviour exactly.
- **Django `runserver` in Docker:** The development server is used inside the container for simplicity. For a production deployment, this should be replaced with Gunicorn + a proper WSGI setup.
- **Frontend served via nginx multi-stage build:** Angular is compiled at Docker build time (not at runtime), so the frontend container is lightweight and serves pre-built static files.

---

## Bonus Features Completed

| Bonus | Status |
|---|---|
| Authentication (login to create prompts) | ❌ Not implemented |
| Tagging system (categorize prompts) | ❌ Not implemented |
| Deployment (publicly accessible) | ❌ Not implemented |

The focus was on building a clean, fully working base application with all core requirements met correctly.

---

## Troubleshooting

**"Failed to load prompts" on the browse page**
```bash
docker-compose exec backend python manage.py makemigrations prompts
docker-compose exec backend python manage.py migrate
```

**Port 4200 or 8000 already in use**
Change the port in `docker-compose.yml`:
```yaml
ports:
  - "4201:80"   # use 4201 instead of 4200
```

**Docker Desktop not running**
Make sure Docker Desktop is open before running `docker-compose up --build`.
