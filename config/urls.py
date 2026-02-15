from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("", lambda request: redirect("products/")),
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls")),
    path("products/", include("products.urls")),
]
