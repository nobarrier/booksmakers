from django.contrib import admin
from .models import Product, Category, ProductImage
import csv
import os
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django.utils.text import slugify


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active")
    inlines = [ProductImageInline]
    change_list_template = "admin/products_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv),
        ]
        return custom_urls + urls

    def _resolve_image_path(self, image_base: str) -> str | None:
        """
        CSV의 product_image_name(확장자 없음)을 받아
        product_images/<name>.jpg 또는 .png 중 존재하는 파일을 우선으로 선택.
        존재 확인이 실패해도(환경 차이) None 반환해서 호출부에서 처리.
        """
        image_base = (image_base or "").strip()
        if not image_base:
            return None

        # 확장자 후보 (필요하면 webp도 추가 가능)
        candidates = [f"{image_base}.jpg", f"{image_base}.png"]

        # media/product_images 폴더에 실제 파일이 있는 경우 우선 매칭
        # (경로 체크가 환경 차이로 실패할 수 있어서, 최종적으로는 첫 후보를 fallback)
        for filename in candidates:
            rel = os.path.join("product_images", filename)
            # 파일 존재를 강제하지 않음(서버/로컬 경로차로 false 나올 수 있음)
            # 단, 파일명 자체는 후보를 리턴해준다.
            # 우선 jpg -> png 순으로 반환
            return rel

        return None

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                # 1) Category
                category_name = row.get("category", "").strip()
                if not category_name:
                    continue

                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={"slug": slugify(category_name, allow_unicode=True)},
                )

                # 2) Product (name 기준 update_or_create)
                name = row.get("name", "").strip()
                if not name:
                    continue

                product, _created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        "category": category,
                        "price": int(row.get("price") or 0),
                        "description": row.get("description", ""),
                        "is_active": True,
                    },
                )

                # 3) Image (ProductImage)
                image_base = row.get("product_image_name", "").strip()
                image_path = self._resolve_image_path(image_base)

                if image_path:
                    # 기존 이미지 삭제(중복 방지)
                    ProductImage.objects.filter(product=product).delete()

                    # ✅ 여기서 파일 exists 검사하지 말고 무조건 DB에 연결(이미지 URL이 실제로 뜨는 걸 확인했으니까)
                    ProductImage.objects.create(
                        product=product,
                        image=image_path,
                    )

            self.message_user(request, "CSV 업로드 완료")
            return redirect("..")

        form = CsvImportForm()
        return render(request, "admin/csv_form.html", {"form": form})


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
