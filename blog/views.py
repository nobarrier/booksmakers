from django.shortcuts import redirect, render
from .models import Category


def home(request):
    categories = Category.objects.all()
    return render(request, "blog/home.html", {"categories": categories})


def category_list(request, slug):
    return redirect("products:category", slug=slug)
