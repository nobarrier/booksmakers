from django.contrib import admin
from .models import Product, Category, ProductImage
import csv
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django.utils.text import slugify


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_number", "price", "is_active")
    inlines = [ProductImageInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                category, _ = Category.objects.get_or_create(
                    name=row["category"],
                    slug=slugify(row["category"], allow_unicode=True),
                )

                Product.objects.create(
                    category=category,
                    name=row["name"],
                    price=int(row["price"]),
                    description=row.get("description", ""),
                    is_active=True,
                )

            self.message_user(request, "CSV 업로드 완료")
            return redirect("..")

        form = CsvImportForm()
        return render(request, "admin/csv_form.html", {"form": form})


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
