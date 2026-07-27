# Quiz Platform

A full-stack quiz platform built with **Django REST Framework** + **React**. Features an admin question bank, a randomized 5-question quiz player, automatic grading, AI-assisted grading for text/image questions, and full attempt history per user.

> Built as a take-home assignment. AI tools (Claude via Hermes) were used to assist with scaffolding and implementation.

---

## Features

- **Guest sessions** — visitors get a JWT-authenticated session automatically, no sign-up required
- **5 question types** — Single choice, Multiple choice, Numerical, Free text, Image upload
- **Auto-grading** — instant, deterministic grading for choice and numerical questions
- **AI grading** — GPT-4o grades free-text answers semantically; GPT-4o Vision grades image uploads (falls back to keyword heuristic when no API key is set)
- **Admin panel** — full CRUD for the question bank with per-type validation
- **Attempt history** — every quiz attempt is persisted and reviewable
- **Accessible** — keyboard navigable, proper ARIA labels, visible focus rings, responsive layout

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5 + Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL 17 |
| Frontend | React (Vite) + Tailwind CSS v4 |
| AI Grading | OpenAI GPT-4o / GPT-4o Vision |
| Deployment | Railway (backend) + Vercel (frontend) |

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 17

### 1. Clone & install

```bash
git clone https://github.com/<your-username>/quiz-platform.git
cd quiz-platform
```

**Backend:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your values
```

Required variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (generate below) |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host (default: `localhost`) |
| `DB_PORT` | PostgreSQL port (default: `5432`) |
| `OPENAI_API_KEY` | OpenAI key for AI grading (set to `stub` to use keyword fallback) |
| `DEBUG` | `True` for local dev, `False` for production |

Generate a secret key:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Set up the database

```bash
# macOS
brew install postgresql@17
brew services start postgresql@17

psql postgres -c "CREATE DATABASE quiz_platform;"
psql postgres -c "CREATE USER quiz_user WITH PASSWORD 'quiz_pass';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE quiz_platform TO quiz_user;"
psql postgres -c "GRANT ALL ON SCHEMA public TO quiz_user;"
psql quiz_platform -c "GRANT ALL ON SCHEMA public TO quiz_user;"
```

### 4. Migrate & seed

```bash
cd backend
python manage.py migrate
python manage.py seed          # loads 25 sample questions
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
# then in Django shell:
python manage.py shell -c "
from apps.users.models import User
u = User.objects.get(username='<your-superuser-name>')
u.is_admin = True
u.save()
print('Admin flag set')
"
```

Admins can access `/login` to sign in with credentials, then navigate to `/admin` for the question bank.

### 6. Run

**Backend** (in `backend/`):
```bash
python manage.py runserver
```

**Frontend** (in `frontend/`):
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) — you'll land directly on the home page as a guest.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/guest/` | None | Create guest session → JWT |
| POST | `/api/auth/login/` | None | Login → JWT |
| POST | `/api/auth/register/` | None | Register account |
| POST | `/api/auth/refresh/` | None | Refresh JWT |
| GET | `/api/auth/me/` | JWT | Current user info |
| GET | `/api/questions/` | JWT | List all questions |
| POST | `/api/questions/` | JWT + admin | Create question |
| PUT | `/api/questions/{id}/` | JWT + admin | Update question |
| DELETE | `/api/questions/{id}/` | JWT + admin | Delete question |
| POST | `/api/attempts/` | JWT | Start new quiz (5 random questions) |
| GET | `/api/attempts/` | JWT | List user's attempts |
| GET | `/api/attempts/{id}/` | JWT | Get attempt detail + answers |
| POST | `/api/attempts/{id}/submit/` | JWT | Submit answers + trigger grading |

---

## Grading System

| Question Type | How it's graded |
|---------------|----------------|
| Single choice | Exact match — selected choice must be the correct one |
| Multiple choice | Exact set match — selected IDs must equal correct IDs |
| Numerical | Float comparison with epsilon tolerance |
| Free text | GPT-4o semantic comparison against model answer (keyword overlap fallback) |
| Image upload | GPT-4o Vision evaluates whether image fulfills the prompt requirement |

Score = number of correct answers out of 5 (0–5).

### Enabling AI grading

Add your OpenAI API key to `backend/.env`:
```
OPENAI_API_KEY=sk-...
```

Without a key (`OPENAI_API_KEY=stub`), text questions use keyword overlap and image questions return a "pending" result.

---

## Seeding Questions

The seed command pre-loads 25 questions covering all 5 types:

```bash
cd backend
python manage.py seed           # add 25 questions
python manage.py seed --clear   # wipe existing and re-seed
```

Categories included: Geography, Science, Math, History, Technology, Biology, Art, Pop Culture.

---

## Tools Used

- **Claude (Anthropic)** via Hermes — scaffolding, architecture decisions, code generation
- **Django REST Framework** — minimized backend boilerplate per spec recommendation
- **djangorestframework-simplejwt** — JWT auth
- **Tailwind CSS v4** — utility-first styling
- **OpenAI GPT-4o** — semantic grading of free-text and image answers

## Time Estimate

~5 hours of development time.
