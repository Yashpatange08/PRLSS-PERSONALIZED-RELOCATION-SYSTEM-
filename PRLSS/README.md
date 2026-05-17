# PRLSS — Personalized Relocation Suggestion System

> **B.Tech Final Year Project** | Django 5 API + React (Vite) Frontend | XGBoost ML | Google Maps

---

## Project Structure

```
prlss-complete/
│
├── prlss-django/               ← Django REST API (Backend)
│   ├── apartment_finder/       ← Django project config
│   ├── recommender/            ← Main app (models, views, ML, admin)
│   ├── data/                   ← CSVs + trained ML model
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── PrlssInterface/             ← React Frontend (Vite)
│   ├── src/
│   │   ├── App.jsx             ← Routes
│   │   ├── Index.jsx           ← Entry point
│   │   ├── Contexts/
│   │   │   └── User.jsx        ← name, budget, city context
│   │   └── Components/
│   │       ├── NavBar.jsx      ← Home | Map | Help | About
│   │       ├── Home.jsx        ← earth.mp4 bg + earth.glb 3D + form
│   │       ├── Map.jsx         ← Google Map + apartment pins
│   │       ├── About.jsx
│   │       ├── Help.jsx
│   │       ├── Cart.jsx        ← (coming soon)
│   │       └── Farman.jsx      ← (coming soon)
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml          ← Run everything with Docker
├── .env.example                ← Copy to .env and fill in keys
└── README.md
```

---

## Quick Start — Docker (60 seconds)

```bash
# 1. Copy env file and add your Google Maps key
cp .env.example .env

# 2. Start Django API + PostgreSQL + Redis
docker-compose up --build

# 3. In a separate terminal — start React frontend
cd PrlssInterface
npm install
npm run dev
```

| Service | URL |
|---------|-----|
| React Frontend | http://localhost:5173 |
| Django API | http://localhost:8000/api/ |
| Admin Panel | http://localhost:8000/admin (admin / admin123) |

---

## Manual Setup (Without Docker)

### Step 1 — Django Backend

```bash
cd prlss-django

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install django djangorestframework django-cors-headers whitenoise joblib scikit-learn numpy pandas

# Run migrations
python manage.py migrate

# Load data (50 apartments + 512 timeline visits)
python manage.py load_data

# Create admin user
python manage.py createsuperuser
# Username: admin | Password: admin123

# Start server
python manage.py runserver
# → http://127.0.0.1:8000
```

### Step 2 — React Frontend

```bash
cd PrlssInterface

# Copy your asset files from RAR into project:
# earth.mp4  → src/earth.mp4
# earth.glb  → public/models/earth.glb
# fonts/*.ttf → src/assets/fonts/

# Copy env and add Google Maps key
cp .env.example .env

# Install and run
npm install
npm run dev
# → http://localhost:5173
```

---

## Adding Your Google Maps Key

1. Go to https://console.cloud.google.com/
2. Create a project → Enable these 3 APIs:
   - Maps JavaScript API
   - Places API
   - Geocoding API
3. Create an API key
4. Open `.env` and set:
   ```
   GOOGLE_MAPS_API_KEY=AIzaSy_your_key_here
   VITE_GOOGLE_MAPS_KEY=AIzaSy_your_key_here
   ```
5. Restart both servers

---

## Copy Your Asset Files

After extracting PrlssInterface.rar, copy these files:

```
From RAR:                          →  Into project:
src/earth.mp4                      →  PrlssInterface/src/earth.mp4
src/models/earth.glb               →  PrlssInterface/public/models/earth.glb
src/assets/fonts/GoogleSans-*.ttf  →  PrlssInterface/src/assets/fonts/
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/recommend/` | Get ML apartment recommendations |
| GET  | `/api/apartments/?city=pune&max_rent=15000` | List apartments |
| GET  | `/api/geocode/?area=Hadapsar&city=pune` | Geocode area name |
| GET  | `/api/autocomplete/?q=ban&city=pune` | Area suggestions |
| GET  | `/api/timeline/` | Timeline clusters |
| POST | `/api/feedback/` | Submit rating |
| GET  | `/api/cities/` | City configs |
| GET  | `/api/stats/` | Live counts |

---

## How the Map.jsx Connects to Django

`Map.jsx` fetches apartments directly from the Django API:

```javascript
fetch(`http://127.0.0.1:8000/api/apartments/?city=${city}&max_rent=${budget}`)
```

CORS is already configured in Django to allow requests from `localhost:5173`.

---

*PRLSS v2 | Django 5 + React + XGBoost + Google Maps*
