# Canteen Management System

Updated: 2026-03-12

This repository contains a Django-based Canteen Management System for students, teachers, and canteen administrators. The project supports local development with SQLite or PostgreSQL, AJAX-powered live dashboard refreshes, and production deployment to Railway with PostgreSQL, WhiteNoise, Gunicorn, and a persistent media volume.

## Core Features

- Role-based login for students, teachers, and canteen admins
- Menu browsing with live stock refresh through AJAX polling
- Cart and checkout flow with receipt generation
- Admin inventory management, quick edit tools, and sales analytics
- Image upload support for menu items
- Railway-ready production settings with PostgreSQL and persistent uploaded media storage

## Technology Stack

- Python 3.12
- Django 5.2.11
- SQLite for default local development
- PostgreSQL for Railway production
- Gunicorn for production serving
- WhiteNoise for static files
- Vanilla JavaScript for AJAX polling and form interactivity

## Project Structure

```text
/home/suhan/CMS/
├── accounts/
├── canteen_management/
│   ├── base.py
│   ├── local.py
│   ├── media_views.py
│   ├── production.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── home/
├── inventory/
├── orders/
├── payments/
├── public/
├── data-migration.json
├── manage.py
├── Procfile
├── requirements.txt
└── runtime.txt
```

## Local Installation

1. Create and activate a virtual environment.

```bash
python3 -m venv myenv
source myenv/bin/activate
```

1. Install dependencies.

```bash
pip install -r requirements.txt
```

1. Create a local environment file.

```bash
cp .env.example .env
```

1. Set a local secret key in `.env`.

```env
DJANGO_ENV=local
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

1. Choose your local database mode.

SQLite default:

- Leave `DATABASE_URL` unset.
- Django will use `db.sqlite3` automatically.

Local PostgreSQL optional:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/canteen_management
DB_CONN_MAX_AGE=600
DB_SSL_REQUIRE=False
```

Automated tests default to SQLite even if DATABASE_URL is set. If you want tests to run against PostgreSQL, set TEST_DATABASE_URL explicitly.

```env
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/canteen_management_test
```

1. Set the local media path.

```env
DJANGO_MEDIA_URL=/media/
DJANGO_MEDIA_ROOT=/home/your-user/CMS/public/media
```

1. Run migrations and start the server.

```bash
python manage.py migrate
python manage.py runserver
```

## Settings Split

The project now uses a clean settings split:

- `canteen_management/settings.py`: environment switcher
- `canteen_management/base.py`: shared settings
- `canteen_management/local.py`: local development settings
- `canteen_management/production.py`: Railway production settings

Environment selection is controlled by `DJANGO_ENV`.

- `DJANGO_ENV=local` loads local settings
- `DJANGO_ENV=production` loads Railway-safe production settings

## Secret Key Management

Local development:

- Store `DJANGO_SECRET_KEY` only inside `.env`
- `.env` is ignored by Git
- `.env.example` stays committed as the template

Railway production:

- Do not commit the real production key
- Generate a new key locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- Paste that generated value into the Railway web service variable `DJANGO_SECRET_KEY`

## AJAX Features

The app uses silent background polling instead of WebSockets.

- Customer menu data refresh endpoint: `/api/inventory/`
- Admin inventory refresh endpoint: `/admin_page/api/inventory/`
- Admin analytics refresh endpoint: `/admin_page/analytics/api/`
- Admin orders refresh endpoint: `/admin_page/orders/api/`

Polling keeps inventory, analytics, and order data fresh without showing extra UI text about the refresh interval.

## SQLite to PostgreSQL Migration

If your existing data is currently in SQLite, use the committed fixture file.

```bash
python manage.py migrate
python manage.py loaddata data-migration.json
```

`data-migration.json` is intentionally tracked in Git so Railway can seed the live PostgreSQL database after first deployment.

## Railway Deployment Files

This project uses the following root deployment files:

- `requirements.txt`
- `Procfile`
- `runtime.txt`

Required packages already included:

- `gunicorn`
- `psycopg2-binary`
- `whitenoise`
- `dj-database-url`
- `python-dotenv`

## Production Media Storage

Railway containers are ephemeral, so uploaded files must not stay on the container filesystem alone.

Production uses:

- `MEDIA_URL=/media/`
- `MEDIA_ROOT=/app/media`

You must attach a Railway Persistent Volume mounted at `/app/media`.

## Verification Commands

Run these before pushing to GitHub:

```bash
python manage.py check
python manage.py test
python manage.py collectstatic --noinput
```

When DJANGO_ENV=local, the test command uses SQLite by default so it does not depend on Railway or another managed PostgreSQL user being allowed to create test databases.

## Deployment Help

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for the full Railway deployment sequence and [DBMS_VIVA_GUIDE.md](DBMS_VIVA_GUIDE.md) for viva preparation notes.
