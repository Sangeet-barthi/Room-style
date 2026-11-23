# RoomStyle Django

A Django app that accepts a room photo and uses the Gemini API to generate interior-design recommendations.

## Requirements

- Python 3.12
- A Gemini API key
- A PostgreSQL database and Cloudinary account for Vercel deployments

## Local setup

1. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a local `.env` from `.env.example`, or add its settings to an existing `.env`. Set a private `DJANGO_SECRET_KEY` and your `GEMINI_API_KEY`. Never commit `.env`.

4. Apply migrations and start Django:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

Open `http://127.0.0.1:8000/` in your browser.

Locally, Django uses SQLite and filesystem media storage unless `DATABASE_URL` or `CLOUDINARY_URL` is set. Uploaded images and the local SQLite database are excluded from Git.

## Vercel configuration

Vercel's deployment filesystem is read-only and ephemeral. Configure these environment variables in the Vercel project settings; use the actual values from your providers and do not commit them:

- `DATABASE_URL`: a persistent PostgreSQL connection URL. The deployment requires this instead of SQLite.
- `CLOUDINARY_URL`: Cloudinary's API URL in the form `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`. This keeps uploaded room photos available to the homepage and analysis history.
- `DJANGO_SECRET_KEY` and `GEMINI_API_KEY`: the Django and Gemini secrets used by the app.

Set the variables for each Vercel environment you deploy (Production, Preview, and Development as applicable), then redeploy. Before using the deployed app, run `python manage.py migrate` with `DATABASE_URL` set to the hosted PostgreSQL database. The app does not have schema changes from this update; this applies any existing migrations to the new database.
