<img width="1352" height="605" alt="image" src="https://github.com/user-attachments/assets/f413eff7-a4a0-4859-9887-81adf1e932c3" />
# Skycast — Weather Website

A responsive Python/Flask weather page. Enter a state, city, and district to see current conditions and a five-day outlook.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Weather data provider

The app uses [Open-Meteo](https://open-meteo.com/) for both location search and forecasts. The provider currently requires no API key for non-commercial use. `app.py` keeps location lookup and weather retrieval in separate functions (`find_location` and `get_weather`) so you can replace either with another provider's API later. Review the provider's current usage terms before publishing or using this commercially.

The location lookup supports locations worldwide. Enter the country, city, and state/region; district is used to help rank possible matches. Some countries do not use state or district divisions, and geocoding results may omit a district, so check the displayed matched location if names are ambiguous.

## Deploy / Git

Push this folder to your Git repository. For a hosting service, set its Python version to 3.10+ and install `requirements.txt`; configure the start command as `gunicorn app:app` (and add `gunicorn` to `requirements.txt` if your host requires it). Set a random `SECRET_KEY` environment variable in production. Do not commit secrets.

## Project structure

- `app.py` — Flask routes, provider requests, and weather formatting
- `templates/index.html` — form and results layout
- `static/styles.css` — responsive styling
- `static/app.js` — form feedback and local date formatting
- `requirements.txt` — Python packages


