import csv
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recommender.models import Apartment, TimelineVisit


class Command(BaseCommand):
    help = "Load apartment and timeline CSV data into the database."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete existing records first")
        parser.add_argument("--city", default="nashik", help="City slug (default: nashik)")
        parser.add_argument("--apartments-only", action="store_true")

    def handle(self, *args, **options):
        city  = options["city"]
        clear = options["clear"]

        if clear:
            Apartment.objects.filter(city=city).delete()
            TimelineVisit.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing data cleared."))

        # Apartments
        apt_path = settings.APARTMENTS_CSV_PATH
        if not apt_path.exists():
            raise CommandError(f"Apartments CSV not found: {apt_path}")

        created = 0
        with open(apt_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                _, made = Apartment.objects.update_or_create(
                    name=row["name"].strip(), city=city,
                    defaults={
                        "lat":           float(row["lat"]),
                        "lon":           float(row["lon"]),
                        "rent":          int(float(row["rent"])),
                        "college_dist":  float(row["college_dist"]),
                        "grocery_dist":  float(row["grocery_dist"]),
                        "amenity_score": float(row["amenity_score"]),
                        "value_score":   float(row["value_score"]),
                        "is_active":     True,
                    },
                )
                if made:
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Apartments: {created} created / {Apartment.objects.filter(city=city).count()} total"
        ))

        if options.get("apartments_only"):
            return

        # Timeline
        tl_path = settings.TIMELINE_CSV_PATH
        if not tl_path.exists():
            self.stdout.write(self.style.WARNING("Timeline CSV not found — skipping."))
            return

        processed = 0
        with open(tl_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                TimelineVisit.objects.get_or_create(
                    lat=round(float(row["lat"]), 5),
                    lon=round(float(row["lon"]), 5),
                    defaults={
                        "visit_freq": int(float(row.get("visit_freq", 1))),
                        "cluster":    int(float(row.get("cluster", 0))),
                    },
                )
                processed += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Timeline: {processed} visits / {TimelineVisit.objects.count()} total"
        ))
        self.stdout.write(self.style.SUCCESS("🎉 Data loading complete!"))
