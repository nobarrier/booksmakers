from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category
from django.db.models import Q


def home(request):
    q = request.GET.get("q", "").strip()  # ✅ 검색어 받기

    products = Product.objects.filter(is_active=True).prefetch_related("images")

    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(category__name__icontains=q)
            | Q(brand__icontains=q)
            | Q(serial_number__icontains=q)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(parent__isnull=True)

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": page_obj,
            "categories": categories,
            "q": q,  # ✅ 템플릿으로 검색어 전달
        },
    )


def category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    q = request.GET.get("q", "").strip()  # ✅ 검색어 받기

    ancestors = category.get_ancestors()
    depth1 = ancestors[0] if len(ancestors) >= 1 else category
    depth2 = ancestors[1] if len(ancestors) >= 2 else None

    descendant_ids = category.get_descendant_ids()

    products = Product.objects.filter(
        category_id__in=descendant_ids, is_active=True
    ).prefetch_related("images")

    if q:
        products = products.filter(name__icontains=q)  # ✅ 검색 적용

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(parent__isnull=True)

    return render(
        request,
        "catalog/product_list.html",
        {
            "category": category,
            "products": page_obj,
            "categories": categories,
            "depth1": depth1,
            "depth2": depth2,
            "ancestors": ancestors,
            "q": q,  # ✅ 전달
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    categories = Category.objects.filter(parent__isnull=True)

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "categories": categories,
        },
    )
