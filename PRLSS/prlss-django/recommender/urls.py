from django.urls import path
from .views import (
    RecommendView, ApartmentListView, TimelineListView,
    FeedbackCreateView, stats_view,
    geocode_view, autocomplete_view,
    CityListView, city_detail,
)

urlpatterns = [
    # Cities — from database (all Indian cities)
    path("cities/",            CityListView.as_view(), name="api-cities"),
    path("cities/<slug:slug>/", city_detail,           name="api-city-detail"),

    # Core endpoints
    path("recommend/",    RecommendView.as_view(),      name="api-recommend"),
    path("apartments/",   ApartmentListView.as_view(),  name="api-apartments"),
    path("timeline/",     TimelineListView.as_view(),   name="api-timeline"),
    path("feedback/",     FeedbackCreateView.as_view(), name="api-feedback"),
    path("stats/",        stats_view,                   name="api-stats"),

    # Google Maps
    path("geocode/",      geocode_view,                 name="api-geocode"),
    path("autocomplete/", autocomplete_view,            name="api-autocomplete"),
]
