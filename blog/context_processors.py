
from .models import Category

def category_menu(request):
    return {
        "categories": Category.objects.all()
    }
