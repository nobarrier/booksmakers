import os
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


def product_image_path(instance, filename):
    """
    저장 경로:
    media/product_images/MCU/BK-MCU-0001/BK-MCU-0001_img_01.jpg
    """

    category_code = instance.serial_number.split("-")[1]
    serial = instance.serial_number

    return f"product_images/{category_code}/{serial}/{filename}"


class Product(models.Model):
    serial_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
    )

    category = models.ForeignKey(
        "catalog.Category",
        related_name="products",
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


def thumbnail(self):
    thumb = self.images.filter(is_thumbnail=True).first()
    if thumb:
        return thumb.image.url
    first = self.images.first()
    if first:
        return first.image.url
    return None


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=product_image_path)
    is_thumbnail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} Image"
