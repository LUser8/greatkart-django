from .models import Category


def menu_list(request):
    categories = Category.objects.all()
    return dict(categories=categories)