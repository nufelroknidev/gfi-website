"""
Load scraped products from scrape_output.json into the database.
Usage: python manage.py load_scraped_products [--json scrape_output.json] [--dry-run]
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.products.models import Category, Product


class Command(BaseCommand):
    help = "Load scraped products from scrape_output.json, replacing all existing products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            default="scrape_output.json",
            help="Path to the scraped JSON file (default: scrape_output.json)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate data without writing to the database.",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json"])
        dry_run = options["dry_run"]

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {json_path}"))
            return

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        self.stdout.write(f"Loaded {len(data)} products from {json_path}")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no database changes"))
            cats = {}
            for p in data:
                cats[p["category"]] = cats.get(p["category"], 0) + 1
            for cat, count in sorted(cats.items()):
                self.stdout.write(f"  {cat}: {count}")
            return

        # --- Clear existing products and categories ---
        deleted_products, _ = Product.objects.all().delete()
        deleted_cats, _ = Category.objects.all().delete()
        self.stdout.write(
            self.style.WARNING(f"Cleared {deleted_products} products and {deleted_cats} categories")
        )

        # --- Create categories ---
        category_order = [
            "Sweeteners", "Acidulants", "Thickeners", "Emulsifiers",
            "Preservatives", "Antioxidants", "Flavorings", "Proteins",
            "Amino Acids", "Vitamins", "Phosphates", "Plant Extracts",
            "Enzymes", "Nutritional Supplements", "Cocoa Series",
            "Dehydrated Vegetables", "Surfactants", "Others",
        ]
        categories = {}
        used_cats = {p["category"] for p in data}
        for i, name in enumerate(category_order):
            if name not in used_cats:
                continue
            slug = slugify(name)
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "order": i + 1},
            )
            categories[name] = cat

        self.stdout.write(f"Created {len(categories)} categories")

        # --- Create products ---
        created = 0
        skipped = 0
        used_slugs = set()

        for item in data:
            cat_name = item.get("category", "Others")
            cat = categories.get(cat_name)
            if not cat:
                self.stderr.write(f"  Unknown category '{cat_name}' — skipping {item['name']}")
                skipped += 1
                continue

            name = item.get("name", "").strip()
            if not name:
                skipped += 1
                continue

            # Generate unique slug
            base_slug = slugify(name)[:200]
            slug = base_slug
            counter = 1
            while slug in used_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            used_slugs.add(slug)

            Product.objects.create(
                category=cat,
                name=name,
                slug=slug,
                cas_number=item.get("cas_number", "")[:50],
                description=item.get("description", ""),
                specifications=item.get("specifications", ""),
                available_forms=item.get("available_forms", "")[:200],
                is_active=True,
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created} products created, {skipped} skipped"
            )
        )
