from django.conf import settings


def google_maps_key(request):
    """
    Injects Google Maps API key into all Django templates.
    CITY_CONFIG removed — cities are now in the DB.
    """
    return {
        "GOOGLE_MAPS_API_KEY": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
        "DEFAULT_CITY":        getattr(settings, "DEFAULT_CITY", "nashik"),
    }
