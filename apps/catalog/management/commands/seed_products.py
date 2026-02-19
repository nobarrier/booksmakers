from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product
import random


class Command(BaseCommand):
    help = "Create dummy products for each category"

    def handle(self, *args, **kwargs):
        categories = Category.objects.all()

        if not categories.exists():
            self.stdout.write(self.style.ERROR("No categories found"))
            return

        for category in categories:
            for i in range(1, 6):
                Product.objects.create(
                    category=category,
                    name=f"{category.name} 상품 {i}",
                    price=random.randint(10000, 150000),
                    description=f"{category.name} 관련 더미 상품입니다.",
                    is_active=True,
                )

        self.stdout.write(self.style.SUCCESS("Dummy products created successfully"))
