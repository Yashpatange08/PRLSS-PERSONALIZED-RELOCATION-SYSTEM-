from rest_framework import serializers
from django.conf import settings
from .models import Apartment, TimelineVisit, UserPreference, RecommendationFeedback


class ApartmentSerializer(serializers.ModelSerializer):
    match_percent = serializers.SerializerMethodField()
    city_display  = serializers.CharField(source="get_city_display", read_only=True)

    class Meta:
        model  = Apartment
        fields = [
            "id", "name", "city", "city_display", "lat", "lon", "address",
            "rent", "college_dist", "grocery_dist", "amenity_score",
            "value_score", "match_percent", "furnished", "bhk", "contact", "is_active",
        ]

    def get_match_percent(self, obj):
        return obj.match_percent


class TimelineVisitSerializer(serializers.ModelSerializer):
    cluster_label = serializers.SerializerMethodField()

    class Meta:
        model  = TimelineVisit
        fields = ["id", "lat", "lon", "visit_freq", "cluster", "cluster_label", "place_name"]

    def get_cluster_label(self, obj):
        return TimelineVisit.CLUSTER_LABELS.get(obj.cluster, f"Cluster {obj.cluster}")


class RecommendRequestSerializer(serializers.Serializer):
    name        = serializers.CharField(max_length=100)
    mobile      = serializers.CharField(max_length=15, required=False, default="")
    area_name   = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    college_lat = serializers.FloatField(required=False, allow_null=True, default=None)
    college_lon = serializers.FloatField(required=False, allow_null=True, default=None)
    rent_budget = serializers.IntegerField(min_value=1000, max_value=200000)
    city        = serializers.ChoiceField(choices=["nashik", "mumbai", "pune"], default="nashik")

    def validate(self, data):
        has_area   = bool(data.get("area_name", "").strip())
        has_coords = (data.get("college_lat") is not None and
                      data.get("college_lon") is not None)
        if not has_area and not has_coords:
            raise serializers.ValidationError(
                "Provide either 'area_name' or 'college_lat' + 'college_lon'."
            )
        city_cfg = settings.CITY_CONFIG.get(data["city"], {})
        max_rent = city_cfg.get("max_rent", 200000)
        if data["rent_budget"] > max_rent:
            raise serializers.ValidationError({
                "rent_budget": f"Budget exceeds max ₹{max_rent:,} for {data['city'].title()}."
            })
        return data


class GeocodeRequestSerializer(serializers.Serializer):
    area = serializers.CharField(max_length=200)
    city = serializers.ChoiceField(choices=["nashik", "mumbai", "pune"], default="nashik")


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model        = UserPreference
        fields       = ["id", "name", "mobile", "city", "college_lat",
                        "college_lon", "rent_budget", "result_snapshot", "created_at"]
        read_only_fields = ["id", "created_at"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model        = RecommendationFeedback
        fields       = ["id", "user_pref", "apartment", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
