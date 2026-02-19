from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<str:category_slug>/", views.category, name="category"),
    path("<int:pk>/", views.product_detail, name="detail"),
]
