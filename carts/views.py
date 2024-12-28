from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
import locale
from django.contrib.auth.decorators import login_required

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
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    try:
        # Lấy giỏ hàng qua session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        existing_variation_list = []
        id_list = []
        for item in cart_item:
            existing_variation = item.variations.all()
            existing_variation_list.append(list(existing_variation))
            id_list.append(item.id)

        # So sánh danh sách variation dựa trên giá trị (dùng set để so sánh không cần thứ tự)
        if any(
            set(product_variation) == set(existing_variation)
            for existing_variation in existing_variation_list
        ):
            # Nếu đã tồn tại, tăng số lượng
            index = next(
                i
                for i, existing_variation in enumerate(existing_variation_list)
                if set(product_variation) == set(existing_variation)
            )
            item_id = id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            # Nếu chưa tồn tại, tạo mới
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        # Tạo mới nếu chưa có sản phẩm nào trong giỏ
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if product_variation:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect("cart")


def increase_quantity(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    # Lấy danh sách tất cả CartItem liên quan đến product và cart hiện tại
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    # Tìm đúng CartItem dựa trên variations
    product_variation = []
    if request.method == "POST":
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    for cart_item in cart_items:
        existing_variation = list(cart_item.variations.all())
        if set(existing_variation) == set(product_variation):
            # Nếu tìm thấy CartItem phù hợp, tăng số lượng
            if cart_item.quantity < 99:  # Giới hạn tối đa
                cart_item.quantity += 1
                cart_item.save()
            break
    else:
        # Nếu không tìm thấy, tạo mới một CartItem với các variations tương ứng
        new_cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if product_variation:
            new_cart_item.variations.set(product_variation)
        new_cart_item.save()

    return redirect("cart")


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    # Lấy danh sách tất cả CartItem liên quan đến product và cart hiện tại
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    # Tìm đúng CartItem dựa trên variations
    product_variation = []
    if request.method == "POST":
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    for cart_item in cart_items:
        existing_variation = list(cart_item.variations.all())
        if set(existing_variation) == set(product_variation):
            # Nếu tìm thấy CartItem phù hợp, giảm số lượng
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                # Nếu số lượng là 1, xóa CartItem
                cart_item.delete()
            break

    return redirect("cart")


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    # Lấy danh sách các CartItem liên quan đến product và cart hiện tại
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    # Xác định đúng CartItem dựa trên variations từ POST
    product_variation = []
    if request.method == "POST":
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    for cart_item in cart_items:
        existing_variation = list(cart_item.variations.all())
        if set(existing_variation) == set(product_variation):
            # Nếu tìm thấy CartItem phù hợp, xóa nó
            cart_item.delete()
            break

    return redirect("cart")


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        shipping_fee = 0
        grand_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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

            # Lấy hình ảnh chính của sản phẩm
            main_image = cart_item.product.images.filter(is_main=True).first()

            # Sắp xếp variations theo variation_category (Color trước, Size sau)
            sorted_variations = cart_item.variations.all().order_by(
                "variation_category"
            )

            cart_items_with_images.append(
                {
                    "cart_item": cart_item,
                    "main_image": main_image.image.url if main_image else None,
                    "product_url": product_url,
                    "sorted_variations": sorted_variations,
                }
            )

        # Nếu tổng giá trị <= 200.000đ thì tính phí vận chuyển 25.000đ
        if total <= 200000:
            shipping_fee = 25000

        grand_total = total + shipping_fee

        # Định dạng lại theo tiền Việt Nam
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


@login_required(login_url="login")
def checkout(request, total=0, quantity=0, cart_items=None):
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

            # Lấy hình ảnh chính của sản phẩm
            main_image = cart_item.product.images.filter(is_main=True).first()

            # Sắp xếp variations theo variation_category (Color trước, Size sau)
            sorted_variations = cart_item.variations.all().order_by(
                "variation_category"
            )

            cart_items_with_images.append(
                {
                    "cart_item": cart_item,
                    "main_image": main_image.image.url if main_image else None,
                    "product_url": product_url,
                    "sorted_variations": sorted_variations,
                }
            )

        # Nếu tổng giá trị <= 200.000đ thì tính phí vận chuyển 25.000đ
        if total <= 200000:
            shipping_fee = 25000

        grand_total = total + shipping_fee

        # Định dạng lại theo tiền Việt Nam
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
    return render(request, "store/checkout.html", context)
