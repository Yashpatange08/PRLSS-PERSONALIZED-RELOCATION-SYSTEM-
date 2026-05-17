from django.conf import settings

def google_maps_key(request):
    return {
        "GOOGLE_MAPS_API_KEY": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
        "CITY_CONFIG":         getattr(settings, "CITY_CONFIG", {}),
        "DEFAULT_CITY":        getattr(settings, "DEFAULT_CITY", "nashik"),
    }
