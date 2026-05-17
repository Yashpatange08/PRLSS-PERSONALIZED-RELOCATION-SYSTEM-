from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds the City model to support all Indian cities.
    Does NOT touch existing Apartment, Timeline, UserPreference, Feedback tables.
    """

    dependencies = [
        ("recommender", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(db_index=True, max_length=100)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("state_name", models.CharField(max_length=100)),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("population", models.BigIntegerField(default=0)),
                ("tier", models.CharField(
                    choices=[("metro","Metro"),("tier1","Tier 1"),("tier2","Tier 2"),("tier3","Tier 3")],
                    default="tier2",
                    max_length=10,
                )),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "City",
                "verbose_name_plural": "Cities",
                "ordering": ["name"],
            },
        ),
    ]
