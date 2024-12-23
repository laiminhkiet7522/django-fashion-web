from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import locale

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            print(key, value)

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except:
                pass

    try:
        # Lấy giỏ hàng bằng cách sử dụng cart_id có trong session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            for item in product_variation:
                cart_item.variations.add(item)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            for item in product_variation:
                cart_item.variations.add(item)
        cart_item.save()

    return redirect("cart")


def remove_cart(request, product_id):

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect("cart")


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()
    return redirect("cart")


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        shipping_fee = 0
        grand_total = 0

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        cart_items_with_images = []

        for cart_item in cart_items:
            product_price = (
                cart_item.product.discount_price
                if cart_item.product.discount_price
                else cart_item.product.price
            )
            total += product_price * cart_item.quantity
            quantity += cart_item.quantity

            # Gọi hàm get_url từ product và thêm vào context
            product_url = cart_item.product.get_url()

            main_image = cart_item.product.images.filter(is_main=True).first()
            cart_items_with_images.append(
                {
                    "cart_item": cart_item,
                    "main_image": main_image.image.url if main_image else None,
                    "product_url": product_url,
                }
            )

        # Nếu đơn hàng có giá trị nhỏ hơn bằng 200.000đ thì tính phí vận chuyển là 25.000đ
        if total <= 200000:
            shipping_fee = 25000

        grand_total = total + shipping_fee

        # Định dạng lại theo hiển thị kiểu tiền Việt Nam
        locale.setlocale(locale.LC_ALL, "vi_VN.UTF-8")
        formatted_total = locale.format_string("%d", total, grouping=True) + "đ"
        formatted_grand_total = (
            locale.format_string("%d", grand_total, grouping=True) + "đ"
        )
        formatted_shipping_fee = (
            locale.format_string("%d", shipping_fee, grouping=True) + "đ"
        )

    except ObjectDoesNotExist:
        cart_items_with_images = []
        formatted_total = "0đ"
        formatted_grand_total = "0đ"
        formatted_shipping_fee = "0đ"

    context = {
        "total": total,
        "formatted_total": formatted_total,
        "formatted_grand_total": formatted_grand_total,
        "formatted_shipping_fee": formatted_shipping_fee,
        "quantity": quantity,
        "cart_items": cart_items_with_images,
    }
    return render(request, "store/cart.html", context)
