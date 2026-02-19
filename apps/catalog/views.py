from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def home(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(parent__isnull=True)

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": products,
            "categories": categories,
        },
    )


def category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_active=True)

    categories = Category.objects.filter(parent__isnull=True)

    return render(
        request,
        "catalog/product_list.html",
        {
            "category": category,
            "products": products,
            "categories": categories,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    categories = Category.objects.filter(parent__isnull=True)

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "categories": categories,
        },
    )
