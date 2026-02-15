from django.shortcuts import get_object_or_404, render
from blog.models import Category
from .models import Product


def product_list(request, slug=None):
    category = None
    products = Product.objects.filter(is_active=True).select_related("category")

    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

    return render(
        request,
        "products/product_list.html",
        {
            "category": category,
            "products": products,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pk,
        is_active=True,
    )
    return render(request, "products/product_detail.html", {"product": product})
