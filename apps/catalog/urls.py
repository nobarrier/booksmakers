from django.urls import path
from . import views
from .views import product_price_compare

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<str:category_slug>/", views.category, name="category"),
    path("<int:pk>/", views.product_detail, name="detail"),
    # 🔥 가격비교 API
    path("compare/<slug:slug>/", product_price_compare, name="compare"),
]
