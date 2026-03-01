# shift. — Air Quality Dashboard · Django Backend

## Endpoints

### Auth (`/api/auth/`)
| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/register/` | Public | Create account, returns JWT tokens |
| POST | `/login/` | Public | Returns access + refresh tokens + user info |
| POST | `/logout/` | Bearer | Blacklist refresh token |
| POST | `/token/refresh/` | — | Get new access token from refresh |
| GET/PATCH | `/profile/` | Bearer | View / update own profile |
| PUT | `/change-password/` | Bearer | Change password |

### AQI (`/api/aqi/`)
| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/stations/` | Optional | List monitoring stations |
| GET | `/stations/<id>/` | Optional | Station detail + latest reading |
| GET | `/readings/?station=<id>` | Optional | Historical readings |
| GET | `/forecast/?station=<id>` | Optional | 24 h forecast |
| GET | `/summary/` | Optional | Dashboard snapshot |
| GET/POST | `/alerts/` | Bearer | List / create user alerts |
| GET/PATCH/DELETE | `/alerts/<id>/` | Bearer | Manage single alert |

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # edit DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Railway deployment

1. Create a Railway project, add a **PostgreSQL** plugin  
2. Add a new service pointing to this repo, set **Root Directory** to `backend/`  
3. Railway auto-injects `DATABASE_URL` — no extra config needed  
4. Set env vars: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`  
5. The `Procfile` `release` command runs migrations + collectstatic on every deploy
