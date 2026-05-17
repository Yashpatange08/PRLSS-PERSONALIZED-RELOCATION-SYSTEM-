from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


# ── NEW: City model replaces hardcoded CITY_CONFIG ───────────────────────────
class City(models.Model):
    """All Indian cities — loaded from india_cities.csv via import_cities command."""
    name       = models.CharField(max_length=100, db_index=True)
    slug       = models.SlugField(max_length=120, unique=True, db_index=True)
    state_name = models.CharField(max_length=100)
    latitude   = models.FloatField()
    longitude  = models.FloatField()
    population = models.BigIntegerField(default=0)
    tier       = models.CharField(
        max_length=10,
        choices=[("metro","Metro"),("tier1","Tier 1"),("tier2","Tier 2"),("tier3","Tier 3")],
        default="tier2",
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering         = ["name"]
        verbose_name     = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name}, {self.state_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ── Existing models UNCHANGED ─────────────────────────────────────────────────

class Apartment(models.Model):
    name          = models.CharField(max_length=200, db_index=True)
    city          = models.CharField(max_length=100, db_index=True)
    lat           = models.FloatField()
    lon           = models.FloatField()
    address       = models.TextField(blank=True)
    rent          = models.PositiveIntegerField()
    college_dist  = models.FloatField(validators=[MinValueValidator(0.0)])
    grocery_dist  = models.FloatField(validators=[MinValueValidator(0.0)])
    amenity_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    value_score   = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    furnished     = models.BooleanField(default=False)
    bhk           = models.PositiveSmallIntegerField(default=1)
    contact       = models.CharField(max_length=15, blank=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rent"]
        indexes  = [
            models.Index(fields=["city", "rent"]),
            models.Index(fields=["city", "value_score"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.city}) - Rs.{self.rent:,}"

    @property
    def match_percent(self):
        return round(self.value_score * 100)


class TimelineVisit(models.Model):
    lat        = models.FloatField()
    lon        = models.FloatField()
    visit_freq = models.PositiveIntegerField(default=1)
    cluster    = models.PositiveSmallIntegerField(default=0)
    place_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    CLUSTER_LABELS = {
        0: "College/Work",
        1: "Market",
        2: "Home",
        3: "Leisure",
        4: "Transport Hub",
    }

    class Meta:
        ordering = ["-visit_freq"]

    def __str__(self):
        label = self.CLUSTER_LABELS.get(self.cluster, f"Cluster {self.cluster}")
        return f"{label} @ ({self.lat:.4f}, {self.lon:.4f})"


class UserPreference(models.Model):
    name            = models.CharField(max_length=100)
    mobile          = models.CharField(max_length=15, blank=True)
    city            = models.CharField(max_length=100)
    college_lat     = models.FloatField()
    college_lon     = models.FloatField()
    rent_budget     = models.PositiveIntegerField()
    result_snapshot = models.JSONField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} | {self.city} | Rs.{self.rent_budget:,}"


class RecommendationFeedback(models.Model):
    user_pref  = models.ForeignKey(UserPreference, on_delete=models.CASCADE, related_name="feedbacks")
    apartment  = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="feedbacks")
    rating     = models.PositiveSmallIntegerField()
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user_pref", "apartment")]
        ordering        = ["-created_at"]

    def __str__(self):
        return f"{self.user_pref.name} -> {self.apartment.name}: {self.rating} stars"
