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


def geocode_area(area_name, city="nashik"):
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return _city_center_fallback(area_name, city)

    city_cfg   = settings.CITY_CONFIG.get(city, {})
    city_name  = city_cfg.get("name", city.title())
    full_query = f"{area_name}, {city_name}, Maharashtra, India"
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
    bounds = settings.CITY_BOUNDS.get(city, {})
    if bounds:
        sw, ne = bounds["sw"], bounds["ne"]
        params["bounds"] = f"{sw['lat']},{sw['lng']}|{ne['lat']},{ne['lng']}"

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
            "city":              city,
            "place_id":          r.get("place_id", ""),
        }
        try:
            cache.set(cache_key, res, timeout=3600)
        except Exception:
            pass
        return res

    logger.warning("Geocode failed for '%s' — status: %s", full_query, status)
    return _city_center_fallback(area_name, city)


def _city_center_fallback(area_name, city):
    cfg = settings.CITY_CONFIG.get(city, settings.CITY_CONFIG["nashik"])
    return {
        "area_name":         area_name,
        "formatted_address": f"{area_name}, {cfg['name']} (approximate)",
        "lat":               cfg["center_lat"],
        "lon":               cfg["center_lon"],
        "city":              city,
        "place_id":          "",
        "is_fallback":       True,
    }


def get_autocomplete_suggestions(query, city="nashik"):
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not api_key or len(query.strip()) < 2:
        return []

    cache_key = f"ac:{city}:{query.lower().strip().replace(' ','_')}"
    cached    = cache.get(cache_key)
    if cached:
        return cached

    city_cfg  = settings.CITY_CONFIG.get(city, {})
    city_name = city_cfg.get("name", city.title())
    bounds    = settings.CITY_BOUNDS.get(city, {})

    params = {
        "input":      f"{query}, {city_name}",
        "key":        api_key,
        "types":      "geocode|establishment",
        "language":   "en",
        "components": "country:in",
    }
    if bounds:
        sw  = bounds["sw"]
        ne  = bounds["ne"]
        params["location"] = f"{(sw['lat']+ne['lat'])/2},{(sw['lng']+ne['lng'])/2}"
        params["radius"]   = "20000"

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
