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
import locale


def payments(request):
    # body = json.loads(request.body)
    # order = Order.objects.get(
    #     user=request.user, is_ordered=False, order_number=body["orderID"]
    # )

    # # Store transaction details inside Payment model
    # payment = Payment(
    #     user=request.user,
    #     payment_id=body["transID"],
    #     payment_method=body["payment_method"],
    #     amount_paid=order.order_total,
    #     status=body["status"],
    # )
    # payment.save()

    # order.payment = payment
    # order.is_ordered = True
    # order.save()

    # # Move the cart items to Order Product table
    # cart_items = CartItem.objects.filter(user=request.user)

    # for item in cart_items:
    #     orderproduct = OrderProduct()
    #     orderproduct.order_id = order.id
    #     orderproduct.payment = payment
    #     orderproduct.user_id = request.user.id
    #     orderproduct.product_id = item.product_id
    #     orderproduct.quantity = item.quantity
    #     orderproduct.product_price = item.product.price
    #     orderproduct.ordered = True
    #     orderproduct.save()

    #     cart_item = CartItem.objects.get(id=item.id)
    #     product_variation = cart_item.variations.all()
    #     orderproduct = OrderProduct.objects.get(id=orderproduct.id)
    #     orderproduct.variations.set(product_variation)
    #     orderproduct.save()

    #     # Reduce the quantity of the sold products
    #     product = Product.objects.get(id=item.product_id)
    #     product.stock -= item.quantity
    #     product.save()

    # # Clear cart
    # CartItem.objects.filter(user=request.user).delete()

    # # Send order recieved email to customer
    # mail_subject = "Thank you for your order!"
    # message = render_to_string(
    #     "orders/order_recieved_email.html",
    #     {
    #         "user": request.user,
    #         "order": order,
    #     },
    # )
    # to_email = request.user.email
    # send_email = EmailMessage(mail_subject, message, to=[to_email])
    # send_email.send()

    # # Send order number and transaction id back to sendData method via JsonResponse
    # data = {
    #     "order_number": order.order_number,
    #     "transID": payment.payment_id,
    # }
    # return JsonResponse(data)
    return render(request, "orders/payments.html")


def place_order(
    request,
    total=0,
    quantity=0,
):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    cart_items_with_variations = []

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

        # Sắp xếp variations theo variation_category (Color trước, Size sau)
        sorted_variations = cart_item.variations.all().order_by("variation_category")

        cart_items_with_variations.append(
            {
                "cart_item": cart_item,
                "sorted_variations": sorted_variations,
            }
        )

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

            # Định dạng lại theo tiền Việt Nam
            locale.setlocale(locale.LC_ALL, "vi_VN.UTF-8")
            formatted_total = locale.format_string("%d", total, grouping=True) + "đ"
            formatted_grand_total = (
                locale.format_string("%d", grand_total, grouping=True) + "đ"
            )
            formatted_shipping_fee = (
                locale.format_string("%d", shipping_fee, grouping=True) + "đ"
            )

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )
            context = {
                "order": order,
                "cart_items": cart_items_with_variations,
                "shipping_fee": shipping_fee,
                "total": total,
                "grand_total": grand_total,
                "formatted_shipping_fee": formatted_shipping_fee,
                "formatted_total": formatted_total,
                "formatted_grand_total": formatted_grand_total,
            }
            return render(request, "orders/payments.html", context)
    else:
        return redirect("checkout")
