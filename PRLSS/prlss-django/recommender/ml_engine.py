import logging
import math
from functools import lru_cache

import joblib
import pandas as pd
from django.conf import settings

logger = logging.getLogger(__name__)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def proximity_score(distance_km, max_km=5.0):
    return math.exp(-distance_km / (max_km / 3))


@lru_cache(maxsize=1)
def load_model():
    path = settings.ML_MODEL_PATH
    if path.exists():
        try:
            model = joblib.load(path)
            logger.info("ML model loaded from %s", path)
            return model
        except Exception as exc:
            logger.error("Failed to load ML model: %s", exc)
    logger.warning("apartment_model.pkl not found — using heuristic fallback")
    return None


def build_features(row, rent_budget):
    rent_norm = float(row["rent"]) / max(rent_budget, 1)
    return pd.DataFrame([{
        "college_dist":  float(row["college_dist"]),
        "grocery_dist":  float(row["grocery_dist"]),
        "amenity_score": float(row["amenity_score"]),
        "rent_norm":     min(rent_norm, 1.0),
    }])


def get_recommendations(college_lat, college_lon, rent_budget, city="nashik", top_n=5):
    from .models import Apartment

    model      = load_model()
    max_radius = getattr(settings, "SEARCH_RADIUS_KM", 5.0)

    qs = Apartment.objects.filter(city=city, is_active=True, rent__lte=rent_budget).values(
        "id", "name", "city", "lat", "lon", "address",
        "rent", "college_dist", "grocery_dist",
        "amenity_score", "value_score", "furnished", "bhk",
    )

    if not qs.exists():
        return []

    df = pd.DataFrame.from_records(qs)
    df["actual_dist_km"] = df.apply(
        lambda r: haversine_km(college_lat, college_lon, r["lat"], r["lon"]), axis=1
    )

    within = df[df["actual_dist_km"] <= max_radius].copy()
    if within.empty:
        within = df[df["actual_dist_km"] <= 10.0].copy()
    if within.empty:
        within = df.copy()

    scores = []
    for _, row in within.iterrows():
        if model is not None:
            try:
                ml_score = float(model.predict(build_features(row, rent_budget))[0])
                ml_score = max(0.0, min(1.0, ml_score))
            except Exception:
                ml_score = float(row["value_score"])
        else:
            ml_score = float(row["value_score"])

        prox  = proximity_score(float(row["actual_dist_km"]), max_km=max_radius)
        match = 0.45 * ml_score + 0.35 * prox + 0.20 * float(row["amenity_score"])
        scores.append(round(min(max(match, 0.0), 1.0), 4))

    within["match_score"] = scores
    top = within.sort_values("match_score", ascending=False).head(top_n)

    result = []
    for _, row in top.iterrows():
        result.append({
            "id":            int(row["id"]),
            "name":          row["name"],
            "city":          row["city"],
            "lat":           float(row["lat"]),
            "lon":           float(row["lon"]),
            "rent":          int(row["rent"]),
            "college_dist":  float(row["actual_dist_km"]),
            "grocery_dist":  float(row["grocery_dist"]),
            "amenity_score": float(row["amenity_score"]),
            "value_score":   float(row["value_score"]),
            "match_score":   float(row["match_score"]),
            "match_percent": round(float(row["match_score"]) * 100),
            "furnished":     bool(row["furnished"]),
            "bhk":           int(row["bhk"]),
        })
    return result
