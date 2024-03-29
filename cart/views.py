from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product, Variation
from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    product_variations = list()
    existing_variation_list = list()
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart.save()
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST.get(key)
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variation)
            except:
                pass

    cart_items = CartItem.objects.filter(product=product, cart=cart)
    cart_item_ids = list()
    if cart_items:
        for cart_item in cart_items:
            cart_item_ids.append(cart_item.id)
            existing_var = cart_item.variations.all()
            existing_variation_list.append(list(existing_var))
        if product_variations in existing_variation_list:
            index = existing_variation_list.index(product_variations)
            cart_item_id = cart_item_ids[index]
            cart_item_ = CartItem.objects.get(product=product, id=cart_item_id)
            cart_item_.quantity += 1
            cart_item_.save()
        else:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            cart_item.variations.add(*product_variations)
            cart_item.save()
    else:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        cart_item.variations.add(*product_variations)
        cart_item.save()
    return redirect('cart')


def remove_cart(request, product_slug, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, slug=product_slug)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    
    return redirect('cart')

def remove_cart_item(request, product_slug, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, slug=product_slug)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity, 
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)
