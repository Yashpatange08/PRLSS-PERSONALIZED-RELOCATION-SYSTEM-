import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .google_maps import geocode_area, get_autocomplete_suggestions, get_place_latlon
from .ml_engine import get_recommendations
from .models import Apartment, City, RecommendationFeedback, TimelineVisit, UserPreference
from .serializers import (
    ApartmentSerializer,
    CitySerializer,
    FeedbackSerializer,
    GeocodeRequestSerializer,
    RecommendRequestSerializer,
    TimelineVisitSerializer,
)

logger = logging.getLogger(__name__)


# ── GET /api/cities/ — ALL Indian cities from DB ──────────────────────────────
class CityListView(generics.ListAPIView):
    """
    Returns all active Indian cities from the database.
    React Home.jsx uses this to populate the city dropdown.
    Supports search: /api/cities/?search=pune
    Supports state filter: /api/cities/?state=Maharashtra
    Supports tier filter: /api/cities/?tier=metro
    """
    serializer_class = CitySerializer

    def get_queryset(self):
        qs     = City.objects.filter(is_active=True)
        search = self.request.query_params.get("search", "").strip()
        state  = self.request.query_params.get("state", "").strip()
        tier   = self.request.query_params.get("tier", "").strip()

        if search:
            qs = qs.filter(name__icontains=search)
        if state:
            qs = qs.filter(state_name__icontains=state)
        if tier:
            qs = qs.filter(tier=tier)

        return qs.order_by("name")[:200]  # cap at 200 for performance


# ── GET /api/cities/<slug>/ — Single city detail ──────────────────────────────
@api_view(["GET"])
def city_detail(request, slug):
    """Returns one city by slug e.g. /api/cities/pune/"""
    try:
        city = City.objects.get(slug=slug, is_active=True)
    except City.DoesNotExist:
        return Response({"error": True, "message": f"City '{slug}' not found."}, status=404)
    return Response({"error": False, "data": CitySerializer(city).data})


# ── POST /api/recommend/ ──────────────────────────────────────────────────────
class RecommendView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = RecommendRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": True, "message": "Invalid input.", "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        city = data["city"]  # city slug or name string

        # Resolve location
        area_name        = data.get("area_name", "").strip()
        lat              = data.get("college_lat")
        lon              = data.get("college_lon")
        resolved_address = ""
        geocode_warning  = ""

        if area_name:
            place_id = request.data.get("place_id", "")
            if place_id:
                place = get_place_latlon(place_id)
                if place:
                    lat = place["lat"]
                    lon = place["lon"]
                    resolved_address = place["formatted_address"]

            if lat is None or lon is None:
                geo = geocode_area(area_name, city)
                if geo:
                    lat = geo["lat"]
                    lon = geo["lon"]
                    resolved_address = geo["formatted_address"]
                    if geo.get("is_fallback"):
                        geocode_warning = (
                            f"Could not precisely locate '{area_name}'. "
                            f"Showing results near {city.title()} center."
                        )
                else:
                    return Response(
                        {"error": True, "message": f"Could not find '{area_name}' in {city.title()}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        if lat is None or lon is None:
            try:
                city_obj = City.objects.get(slug=city)
                lat = float(city_obj.latitude)
                lon = float(city_obj.longitude)
            except City.DoesNotExist:
                lat, lon = 0.0, 0.0

        cache_key = f"recommend:{city}:{lat:.4f}:{lon:.4f}:{data['rent_budget']}"
        cached    = cache.get(cache_key)
        if cached:
            cached["user_name"] = data["name"]
            return Response(cached)

        try:
            recs = get_recommendations(
                college_lat=lat,
                college_lon=lon,
                rent_budget=data["rent_budget"],
                city=city,
                top_n=settings.MAX_RECOMMENDATIONS,
            )
        except Exception as exc:
            logger.exception("ML engine error: %s", exc)
            return Response(
                {"error": True, "message": "Recommendation engine error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        pref = UserPreference.objects.create(
            name=data["name"],
            mobile=data.get("mobile", ""),
            city=city,
            college_lat=lat,
            college_lon=lon,
            rent_budget=data["rent_budget"],
            result_snapshot=recs,
        )

        # Get city display name from DB (fallback to slug title)
        try:
            city_obj      = City.objects.get(slug=city)
            city_display  = str(city_obj)
        except City.DoesNotExist:
            city_display  = city.title()

        top     = recs[0] if recs else None
        payload = {
            "error":             False,
            "user_name":         data["name"],
            "area_name":         area_name,
            "resolved_address":  resolved_address,
            "searched_lat":      lat,
            "searched_lon":      lon,
            "city":              city,
            "city_display":      city_display,
            "rent_budget":       data["rent_budget"],
            "total_found":       len(recs),
            "top_apartment":     top["name"] if top else "None",
            "top_match_percent": top["match_percent"] if top else 0,
            "recommendations":   recs,
            "preference_id":     pref.pk,
            "warning":           geocode_warning,
            "message": (
                f"{data['name']}, top apartment: {top['name']} ({top['match_percent']}% match!)"
                if top else "No apartments found for your criteria."
            ),
        }

        try:
            cache.set(cache_key, payload, timeout=300)
        except Exception:
            pass

        return Response(payload)


# GET /api/geocode/ 
@api_view(["GET"])
def geocode_view(request):
    serializer = GeocodeRequestSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response({"error": True, "detail": serializer.errors}, status=400)
    result = geocode_area(
        serializer.validated_data["area"],
        serializer.validated_data["city"],
    )
    if not result:
        return Response({"error": True, "message": "Could not geocode area."}, status=404)
    return Response({"error": False, "data": result})


#  GET /api/autocomplete/
@api_view(["GET"])
def autocomplete_view(request):
    query = request.query_params.get("q", "").strip()
    city  = request.query_params.get("city", "nashik")
    if not query or len(query) < 2:
        return Response({"error": False, "data": []})
    return Response({"error": False, "data": get_autocomplete_suggestions(query, city)})


# GET /api/apartments/
class ApartmentListView(generics.ListAPIView):
    serializer_class = ApartmentSerializer

    def get_queryset(self):
        qs       = Apartment.objects.filter(is_active=True)
        city     = self.request.query_params.get("city", "")
        max_rent = self.request.query_params.get("max_rent", "")
        if city:
            qs = qs.filter(city=city)
        if max_rent.isdigit():
            qs = qs.filter(rent__lte=int(max_rent))
        return qs.order_by("rent")


# GET /api/timeline/
class TimelineListView(generics.ListAPIView):
    serializer_class = TimelineVisitSerializer

    def get_queryset(self):
        qs      = TimelineVisit.objects.all()
        cluster = self.request.query_params.get("cluster", "")
        if cluster.isdigit():
            qs = qs.filter(cluster=int(cluster))
        return qs.order_by("-visit_freq")[:200]


# POST /api/feedback/ 
class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    queryset         = RecommendationFeedback.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": True, "detail": serializer.errors}, status=400)
        self.perform_create(serializer)
        return Response(
            {"error": False, "message": "Feedback saved!", "data": serializer.data},
            status=201,
        )


# GET /api/stats/
@api_view(["GET"])
def stats_view(request):
    cached = cache.get("prlss:stats")
    if cached:
        return Response(cached)
    data = {
        "total_apartments":      Apartment.objects.filter(is_active=True).count(),
        "total_searches":        UserPreference.objects.count(),
        "total_timeline_visits": TimelineVisit.objects.count(),
        "total_feedbacks":       RecommendationFeedback.objects.count(),
        "total_cities":          City.objects.filter(is_active=True).count(),
        "google_maps_enabled":   bool(getattr(settings, "GOOGLE_MAPS_API_KEY", "")),
    }
    try:
        cache.set("prlss:stats", data, timeout=60)
    except Exception:
        pass
    return Response(data)


#Error Handlers 
def error_400(request, exception=None):
    return HttpResponse('{"error":true,"message":"Bad Request"}',
                        content_type="application/json", status=400)

def error_404(request, exception=None):
    return HttpResponse('{"error":true,"message":"Not Found"}',
                        content_type="application/json", status=404)

def error_500(request):
    return HttpResponse('{"error":true,"message":"Server Error"}',
                        content_type="application/json", status=500)
