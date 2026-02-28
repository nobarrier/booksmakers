import os
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import Sum


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

        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            self.slug = f"{self.parent.slug}-{base_slug}" if self.parent else base_slug

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
        if self.parent and self.parent.get_depth() >= 4:
            raise ValidationError("카테고리는 최대 5단계까지만 허용됩니다.")


def product_image_path(instance, filename):
    serial = instance.product.serial_number
    parts = serial.split("-")
    category_code = parts[1] if len(parts) > 1 else "ETC"
    return f"product_images/{category_code}/{serial}/{filename}"


class Product(models.Model):
    product_code = models.CharField(max_length=50, blank=True)
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


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="variants",
        on_delete=models.CASCADE,
    )

    sku = models.CharField(max_length=100, unique=True)

    cost_price = models.IntegerField(default=0)
    selling_price = models.IntegerField()

    spec_json = models.JSONField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return self.sku

    @property
    def current_stock(self):
        total = self.ledger_entries.aggregate(total=Sum("qty_change"))["total"]
        return total or 0


class Warehouse(models.Model):
    code = models.CharField(max_length=50, unique=True, default="YYCOM_MAIN")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StockLedger(models.Model):
    TYPE_CHOICES = [
        ("PURCHASE_IN", "Purchase In"),
        ("SALE_OUT", "Sale Out"),
        ("ADJUST", "Adjust"),
        ("RESERVE", "Reserve"),
        ("RELEASE", "Release"),
        ("RETURN", "Return"),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        related_name="ledger_entries",
        on_delete=models.CASCADE,
    )

    variant = models.ForeignKey(
        ProductVariant,
        related_name="ledger_entries",
        on_delete=models.CASCADE,
    )

    qty_change = models.IntegerField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.variant.sku} ({self.qty_change})"


class Inventory(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "variant"],
                name="uniq_inventory_warehouse_variant",
            )
        ]
