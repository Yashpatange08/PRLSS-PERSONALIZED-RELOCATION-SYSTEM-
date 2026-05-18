"""
Management command: import_cities
===================================
Loads all Indian cities from india_cities.csv into the City table.

Usage:
    python manage.py import_cities
    python manage.py import_cities --file path/to/custom.csv
    python manage.py import_cities --clear
"""

import csv
from pathlib import Path
from django.utils.text import slugify
from django.core.management.base import BaseCommand
from recommender.models import City


class Command(BaseCommand):
    help = "Import all Indian cities from india_cities.csv into the City table."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=None,
            help="Path to cities CSV (default: data/india_cities.csv)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing cities before importing",
        )

    def handle(self, *args, **options):
        
        if options["file"]:
            csv_path = Path(options["file"])
        else:
            csv_path = Path(__file__).resolve().parents[3] / "data" / "india_cities.csv"

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        if options["clear"]:
            count = City.objects.count()
            City.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing cities."))

        created  = 0
        updated  = 0
        skipped  = 0
        errors   = 0

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validate required fields
                    city_name = row.get("city_name", "").strip()
                    state     = row.get("state_name", "").strip()
                    lat       = float(row.get("latitude", 0))
                    lon       = float(row.get("longitude", 0))

                    if not city_name or not state:
                        skipped += 1
                        continue

                    # Validate coordinates India bounds
                    if not (6.5 <= lat <= 37.5) or not (68.0 <= lon <= 97.5):
                        self.stdout.write(
                            self.style.WARNING(
                                f"Row {row_num}: '{city_name}' has invalid coords ({lat},{lon}) — skipped"
                            )
                        )
                        skipped += 1
                        continue

                    # Generate unique slug
                    base_slug = slugify(city_name)
                    slug      = base_slug
                    counter   = 1
                    
                    while City.objects.filter(slug=slug).exclude(name=city_name).exists():
                        slug = f"{base_slug}-{state[:3].lower()}"
                        counter += 1
                        if counter > 5:
                            slug = f"{base_slug}-{row_num}"
                            break

                    population = int(float(row.get("population", 0) or 0))
                    tier       = row.get("tier", "tier2").strip() or "tier2"

                    city_obj, made = City.objects.update_or_create(
                        name=city_name,
                        defaults={
                            "slug":       slug,
                            "state_name": state,
                            "latitude":   lat,
                            "longitude":  lon,
                            "population": population,
                            "tier":       tier,
                            "is_active":  True,
                        },
                    )

                    if made:
                        created += 1
                    else:
                        updated += 1

                except (ValueError, KeyError) as e:
                    self.stdout.write(
                        self.style.ERROR(f"Row {row_num}: Error — {e}")
                    )
                    errors += 1

        # Summary
        total = City.objects.filter(is_active=True).count()
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Import complete:"
        ))
        self.stdout.write(self.style.SUCCESS(f"  Created : {created}"))
        self.stdout.write(self.style.SUCCESS(f"  Updated : {updated}"))
        self.stdout.write(self.style.WARNING(f"  Skipped : {skipped}"))
        if errors:
            self.stdout.write(self.style.ERROR(f"  Errors  : {errors}"))
        self.stdout.write(self.style.SUCCESS(
            f"  Total active cities in DB: {total}"
        ))
