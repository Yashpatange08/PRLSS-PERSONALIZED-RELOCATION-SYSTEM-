"""
Google Maps Service
====================
Works with ANY Indian city — looks up city center from the City DB table
instead of hardcoded CITY_CONFIG.
"""
import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

GEOCODING_URL    = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES_AC_URL    = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
PLACE_DETAIL_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def _get_json(url, params):
    qs  = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{qs}", headers={"User-Agent": "PRLSS/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        logger.error("Google API request failed: %s", exc)
        return {}


def _get_city_from_db(city_slug):
    """
    Look up city center coords from the City DB table.
    Returns (lat, lon, city_name) or None if not found.
    Works for ALL Indian cities, not just Nashik/Mumbai/Pune.
    """
    try:
        from .models import City
        city_obj = City.objects.filter(
            slug=city_slug, is_active=True
        ).first()
        if city_obj:
            return city_obj.latitude, city_obj.longitude, city_obj.name
        # Try by name if slug not found
        city_obj = City.objects.filter(
            name__iexact=city_slug, is_active=True
        ).first()
        if city_obj:
            return city_obj.latitude, city_obj.longitude, city_obj.name
    except Exception as e:
        logger.warning("City DB lookup failed: %s", e)
    return None


def geocode_area(area_name, city_slug="nashik"):
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return _city_center_fallback(area_name, city_slug)

    # Get city name from DB
    city_db = _get_city_from_db(city_slug)
    city_name = city_db[2] if city_db else city_slug.replace("-", " ").title()

    full_query = f"{area_name}, {city_name}, India"
    cache_key  = f"geocode:{full_query.lower().replace(' ', '_')}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "address":  full_query,
        "key":      api_key,
        "region":   "IN",
        "language": "en",
    }

    #Add bounding box from DB city coords
    if city_db:
        lat, lon, _ = city_db
        #40km bounding box around city center
        delta = 0.4
        params["bounds"] = f"{lat-delta},{lon-delta}|{lat+delta},{lon+delta}"

    data   = _get_json(GEOCODING_URL, params)
    status = data.get("status", "")

    if status == "OK" and data.get("results"):
        r   = data["results"][0]
        loc = r["geometry"]["location"]
        res = {
            "area_name":         area_name,
            "formatted_address": r.get("formatted_address", full_query),
            "lat":               float(loc["lat"]),
            "lon":               float(loc["lng"]),
            "city":              city_slug,
            "place_id":          r.get("place_id", ""),
        }
        try:
            cache.set(cache_key, res, timeout=3600)
        except Exception:
            pass
        return res

    logger.warning("Geocode failed for '%s' — status: %s", full_query, status)
    return _city_center_fallback(area_name, city_slug)


def _city_center_fallback(area_name, city_slug):
    """Uses DB city center coords. Works for all 157 cities."""
    city_db = _get_city_from_db(city_slug)
    if city_db:
        lat, lon, city_name = city_db
    else:
        # Ultimate fallback
        lat, lon, city_name = 20.5937, 78.9629, city_slug.title()

    logger.info("City center fallback for '%s' in %s", area_name, city_name)
    return {
        "area_name":         area_name,
        "formatted_address": f"{area_name}, {city_name} (approximate)",
        "lat":               lat,
        "lon":               lon,
        "city":              city_slug,
        "place_id":          "",
        "is_fallback":       True,
    }


def get_autocomplete_suggestions(query, city_slug="nashik"):
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not api_key or len(query.strip()) < 2:
        return []

    cache_key = f"ac:{city_slug}:{query.lower().strip().replace(' ','_')}"
    cached    = cache.get(cache_key)
    if cached:
        return cached

    city_db   = _get_city_from_db(city_slug)
    city_name = city_db[2] if city_db else city_slug.title()

    params = {
        "input":      f"{query}, {city_name}",
        "key":        api_key,
        "types":      "geocode|establishment",
        "language":   "en",
        "components": "country:in",
    }

    
    if city_db:
        lat, lon, _ = city_db
        params["location"] = f"{lat},{lon}"
        params["radius"]   = "30000"

    data    = _get_json(PLACES_AC_URL, params)
    results = []
    for p in data.get("predictions", [])[:5]:
        sf = p.get("structured_formatting", {})
        results.append({
            "description":    p.get("description", ""),
            "place_id":       p.get("place_id", ""),
            "main_text":      sf.get("main_text", ""),
            "secondary_text": sf.get("secondary_text", ""),
        })
    try:
        cache.set(cache_key, results, timeout=300)
    except Exception:
        pass
    return results


def get_place_latlon(place_id):
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not api_key or not place_id:
        return None

    cache_key = f"place:{place_id}"
    cached    = cache.get(cache_key)
    if cached:
        return cached

    data   = _get_json(PLACE_DETAIL_URL, {
        "place_id": place_id,
        "fields":   "geometry,formatted_address,name",
        "key":      api_key,
    })
    result = data.get("result", {})
    if result:
        loc = result.get("geometry", {}).get("location", {})
        if loc:
            res = {
                "lat":               float(loc["lat"]),
                "lon":               float(loc["lng"]),
                "formatted_address": result.get("formatted_address", ""),
                "name":              result.get("name", ""),
            }
            try:
                cache.set(cache_key, res, timeout=3600)
            except Exception:
                pass
            return res
    return None
