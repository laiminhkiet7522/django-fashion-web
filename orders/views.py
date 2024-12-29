from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderDetail
import json
from products.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def place_order(
    request,
    total=0,
    quantity=0,
):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect("store")

    shipping_fee = 0
    grand_total = 0

    for cart_item in cart_items:
        product_price = (
            cart_item.product.discount_price
            if cart_item.product.discount_price
            else cart_item.product.price
        )
        total += product_price * cart_item.quantity
        quantity += cart_item.quantity
    if total <= 200000:
        shipping_fee = 25000

    grand_total = total + shipping_fee

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone_number = form.cleaned_data["phone_number"]
            data.email = form.cleaned_data["email"]
            data.address = form.cleaned_data["address"]
            data.city = form.cleaned_data["city"]
            data.district = form.cleaned_data["district"]
            data.commune = form.cleaned_data["commune"]
            data.shipping_fee = shipping_fee
            data.order_total = grand_total
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()

            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # order = Order.objects.get(
            #     user=current_user, is_ordered=False, order_number=order_number
            # )
            # context = {
            #     "order": order,
            #     "cart_items": cart_items,
            #     "shipping_fee": shipping_fee,
            #     "total": total,
            #     "grand_total": grand_total,
            # }
            # return render(request, "orders/payments.html", context)
            return redirect("checkout")
    else:
        return redirect("checkout")
