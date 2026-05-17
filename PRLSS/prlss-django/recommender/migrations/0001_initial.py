from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Apartment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(db_index=True, max_length=200)),
                ("city", models.CharField(choices=[("nashik","Nashik"),("mumbai","Mumbai"),("pune","Pune")], db_index=True, default="nashik", max_length=20)),
                ("lat", models.FloatField()),
                ("lon", models.FloatField()),
                ("address", models.TextField(blank=True)),
                ("rent", models.PositiveIntegerField()),
                ("college_dist", models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ("grocery_dist", models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ("amenity_score", models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ("value_score", models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ("furnished", models.BooleanField(default=False)),
                ("bhk", models.PositiveSmallIntegerField(default=1)),
                ("contact", models.CharField(blank=True, max_length=15)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["rent"]},
        ),
        migrations.CreateModel(
            name="TimelineVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("lat", models.FloatField()),
                ("lon", models.FloatField()),
                ("visit_freq", models.PositiveIntegerField(default=1)),
                ("cluster", models.PositiveSmallIntegerField(default=0)),
                ("place_name", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-visit_freq"]},
        ),
        migrations.CreateModel(
            name="UserPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("mobile", models.CharField(blank=True, max_length=15)),
                ("city", models.CharField(choices=[("nashik","Nashik"),("mumbai","Mumbai"),("pune","Pune")], default="nashik", max_length=20)),
                ("college_lat", models.FloatField()),
                ("college_lon", models.FloatField()),
                ("rent_budget", models.PositiveIntegerField()),
                ("result_snapshot", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RecommendationFeedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("user_pref", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="feedbacks", to="recommender.userpreference")),
                ("apartment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="feedbacks", to="recommender.apartment")),
                ("rating", models.PositiveSmallIntegerField()),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="apartment",
            index=models.Index(fields=["city", "rent"], name="apt_city_rent_idx"),
        ),
        migrations.AddIndex(
            model_name="apartment",
            index=models.Index(fields=["city", "value_score"], name="apt_city_vs_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="recommendationfeedback",
            unique_together={("user_pref", "apartment")},
        ),
    ]
