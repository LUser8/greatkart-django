from django.urls import path


from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<slug:product_slug>', views.add_cart, name='add_cart'),
    path('remove_cart/<slug:product_slug>/<int:cart_item_id>', views.remove_cart, name='remove_cart'),
    path('remove_cartitem/<slug:product_slug>/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item')
] 