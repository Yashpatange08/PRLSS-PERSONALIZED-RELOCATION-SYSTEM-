from rest_framework import serializers
from .models import Apartment, City, TimelineVisit, UserPreference, RecommendationFeedback


# City serializer
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = City
        fields = ["id", "name", "slug", "state_name",
                  "latitude", "longitude", "population", "tier"]


#Existing serializers

class ApartmentSerializer(serializers.ModelSerializer):
    match_percent = serializers.SerializerMethodField()

    class Meta:
        model  = Apartment
        fields = [
            "id", "name", "city", "lat", "lon", "address",
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
    rent_budget = serializers.IntegerField(min_value=1000, max_value=500000)
    
    city        = serializers.CharField(max_length=120, default="nashik")

    


class GeocodeRequestSerializer(serializers.Serializer):
    area = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=120, default="nashik")


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
