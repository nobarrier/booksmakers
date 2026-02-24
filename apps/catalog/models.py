import os
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        self.clean()

        # slug 비어있을 때만 생성
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            if self.parent:
                self.slug = f"{self.parent.slug}-{base_slug}"
            else:
                self.slug = base_slug

        super().save(*args, **kwargs)

    def get_ancestors(self):
        nodes = []
        cur = self.parent
        while cur:
            nodes.append(cur)
            cur = cur.parent
        return list(reversed(nodes))

    def get_descendant_ids(self):
        ids = []
        stack = [self]
        while stack:
            node = stack.pop()
            ids.append(node.id)
            stack.extend(list(node.children.all()))
        return ids

    def get_depth(self):
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

    def __str__(self):
        return "—" * self.get_depth() + self.name

    def clean(self):
        # depth는 0부터 시작
        # 0=1차, 1=2차, 2=3차, 3=4차, 4=5차
        if self.parent:
            if self.parent.get_depth() >= 4:
                raise ValidationError("카테고리는 최대 5단계까지만 허용됩니다.")


def product_image_path(instance, filename):
    """
    저장 경로:
    media/product_images/MCU/BK-MCU-0001/BK-MCU-0001_img_01.jpg
    """

    category_code = instance.serial_number.split("-")[1]
    serial = instance.serial_number

    return f"product_images/{category_code}/{serial}/{filename}"


class Product(models.Model):
    serial_number = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
    )

    name = models.CharField(max_length=300)
    brand = models.CharField(max_length=100, blank=True)

    price = models.IntegerField()
    sale_price = models.IntegerField(blank=True, null=True)

    stock = models.IntegerField(default=0)

    short_description = models.CharField(max_length=500, blank=True)
    detail_html = models.TextField(blank=True)

    source_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    is_reviewed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=product_image_path)
    is_thumbnail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} Image"
