from django.db import models


class Product(models.Model):
    category = models.ForeignKey(
        "blog.Category",
        related_name="products",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
