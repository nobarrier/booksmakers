from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Product
from apps.catalog.services.external_api.digikey_api import (
    search_products,
    normalize_products,
)
from apps.catalog.services.category_engine import auto_assign_category


def ensure_unique_slug(base_slug, serial_number):
    slug = slugify(base_slug) or "item"
    candidate = slug
    suffix = 2

    while (
        Product.objects.filter(slug=candidate)
        .exclude(serial_number=serial_number)
        .exists()
    ):
        candidate = f"{slug}-{suffix}"
        suffix += 1

    return candidate


class Command(BaseCommand):
    help = "Import products from DigiKey and save to DB"

    def handle(self, *args, **kwargs):

        raw = search_products("Raspberry Pi")
        products = normalize_products(raw)

        print("\n===== IMPORT START =====\n")

        count = 0

        for item in products:

            serial_number = item["dk_part"] or item["mpn"]
            if not serial_number:
                continue

            # 🔥 자동 분류 적용
            category = auto_assign_category(item)

            slug_value = ensure_unique_slug(
                item["description"] or serial_number,
                serial_number,
            )

            obj, created = Product.objects.update_or_create(
                serial_number=serial_number,
                defaults={
                    "product_code": item["dk_part"] or "",
                    "name": item["description"] or serial_number,
                    "slug": slug_value,
                    "price": item["price"] or 0,
                    "short_description": item["description"] or "",
                    "brand": item["manufacturer"] or "",
                    "source_url": item["url"] or "",
                    "category": category,
                },
            )

            if created:
                print(f"✔ Created: {obj.name}")
            else:
                print(f"↻ Updated: {obj.name}")

            count += 1

        print(f"\n===== DONE ({count} items) =====\n")
