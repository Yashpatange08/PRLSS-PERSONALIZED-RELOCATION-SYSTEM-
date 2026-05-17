from django.urls import path
from .views import (
    RecommendView, ApartmentListView, TimelineListView,
    FeedbackCreateView, city_list, stats_view,
    geocode_view, autocomplete_view,
)

urlpatterns = [
    path("recommend/",    RecommendView.as_view(),      name="api-recommend"),
    path("apartments/",   ApartmentListView.as_view(),  name="api-apartments"),
    path("timeline/",     TimelineListView.as_view(),   name="api-timeline"),
    path("feedback/",     FeedbackCreateView.as_view(), name="api-feedback"),
    path("cities/",       city_list,                    name="api-cities"),
    path("stats/",        stats_view,                   name="api-stats"),
    path("geocode/",      geocode_view,                 name="api-geocode"),
    path("autocomplete/", autocomplete_view,            name="api-autocomplete"),
]
