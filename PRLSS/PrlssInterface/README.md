# PRLSS Interface — React Frontend

## What is this?
React frontend for PRLSS. Connects to the Django backend at `http://127.0.0.1:8000`.

## Structure
```
src/
├── App.jsx               → Routes (Home, Map, Help, About)
├── Index.jsx             → React root entry
├── Index.css             → Global styles + Google Sans fonts
├── Contexts/
│   └── User.jsx          → Stores name, budget, city globally
└── Components/
    ├── NavBar.jsx         → Home | Map | Help | About
    ├── Home.jsx           → earth.mp4 bg + earth.glb 3D + form
    ├── Map.jsx            → Google Map + apartment pins from API
    ├── About.jsx          → About the project
    ├── Help.jsx           → How to use steps
    ├── Cart.jsx           → (coming soon)
    └── Farman.jsx         → (coming soon)
```

## Step 1 — Add your Google Maps Key
```bash
cp .env.example .env
# Open .env and set:
# VITE_GOOGLE_MAPS_KEY=AIzaSy_your_key_here
```

## Step 2 — Copy your asset files from the RAR
Copy these from your original PrlssInterface RAR into this project:
```
src/earth.mp4               → src/earth.mp4
src/models/earth.glb        → src/models/earth.glb  (OR public/models/earth.glb)
src/assets/fonts/*.ttf      → src/assets/fonts/
```

## Step 3 — Install and Run
```bash
npm install
npm run dev
# Opens at http://localhost:5173
```

## Step 4 — Make sure Django is running
```bash
# In your prlss-django folder:
python manage.py runserver
# Runs at http://127.0.0.1:8000
```

## How it connects to Django
Map.jsx fetches apartments from:
```
GET http://127.0.0.1:8000/api/apartments/?city=pune&max_rent=15000
```
