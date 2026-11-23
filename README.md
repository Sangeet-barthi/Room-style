# RoomStyle Django

A Django app that accepts a room photo and uses the Gemini API to generate interior-design recommendations.

## Requirements

- Python 3.12
- A Gemini API key

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

Uploaded images and the SQLite database are local runtime data and are excluded from Git.
