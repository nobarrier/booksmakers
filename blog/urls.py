from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<slug:slug>/", views.category_list, name="category"),
]
