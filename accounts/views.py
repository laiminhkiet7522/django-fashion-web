from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem
from orders.models import Order, OrderDetail
from django.http import HttpResponse
import requests
import locale
from django.utils.timezone import localtime
from django.db.models import Case, When


# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.save()

            # Tạo thông tin người dùng
            profile = UserProfile()
            profile.user_id = user.id
            profile.save()

            # Kích hoạt người dùng
            current_site = get_current_site(request)
            mail_subject = "Kích hoạt tài khoản"
            message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect("/accounts/login/?command=verification&email=" + email)

    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    id_list = []

                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id_list.append(item.id)

                    for pro_var in product_variation:
                        if pro_var in existing_variation_list:
                            index = existing_variation_list.index(pro_var)
                            item_id = id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            auth.login(request, user)
            messages.success(request, "Đăng nhập thành công.")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("dashboard")
        else:
            messages.error(request, "Thông tin đăng nhập không hợp lệ.")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Đăng xuất thành công.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Tài khoản của bạn đã được kích hoạt thành công.")
        return redirect("login")
    else:
        messages.error(request, "Có lỗi xảy ra vui lòng thử lại.")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.filter(user_id=request.user.id, is_ordered=True).order_by(
        "-created_at"
    )
    orders_count = orders.count()
    userprofile = get_object_or_404(UserProfile, user=request.user)

    # Định dạng ngày giờ cho đơn hàng
    formatted_orders = []
    for order in orders:
        formatted_order = {
            "order_number": order.order_number,
            "full_name": order.full_name(),
            "phone_number": order.phone_number,
            "order_total": order.order_total,
            "status": order.status,
            # Chuyển đổi `created_at` sang định dạng Việt Nam
            "created_at": localtime(order.created_at).strftime("%d/%m/%Y %H:%M"),
        }
        formatted_orders.append(formatted_order)

    # Định nghĩa mặc định cho forms
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=userprofile)

    if request.method == "POST":
        if "current_password" in request.POST:
            # Xử lý đổi mật khẩu
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not current_password or not new_password or not confirm_password:
                messages.error(request, "Vui lòng nhập đủ các trường mật khẩu.")
                return redirect("dashboard")

            # Kiểm tra độ dài mật khẩu mới
            if len(new_password) < 6:
                messages.error(request, "Mật khẩu mới phải dài ít nhất 6 ký tự.")
                return redirect("dashboard")

            user = Account.objects.get(username__exact=request.user.username)

            if new_password == confirm_password:
                if user.check_password(current_password):
                    user.set_password(new_password)
                    user.save()
                    messages.success(
                        request,
                        "Mật khẩu đã được đổi mới thành công! Vui lòng đăng nhập lại.",
                    )
                    return redirect("dashboard")
                else:
                    messages.error(request, "Mật khẩu cũ không khớp.")
            else:
                messages.error(
                    request, "Mật khẩu xác nhận không khớp với mật khẩu mới."
                )

        elif "first_name" in request.POST:
            # Xử lý cập nhật thông tin cá nhân
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, instance=userprofile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Thông tin đã được cập nhật thành công.")
                return redirect("dashboard")
        else:
            messages.error(request, "Yêu cầu không hợp lệ.")

    context = {
        "orders_count": orders_count,
        "my_order": formatted_orders,
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }
    return render(request, "accounts/dashboard.html", context)


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = "Đặt lại mật khẩu"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request,
                "Yêu cầu đặt lại mật khẩu đã được gửi đến địa chỉ email của bạn. Vui lòng kiểm tra trong hộp thư đến (kể cả hộp thư rác).",
            )
            return redirect("forgotPassword")
        else:
            messages.error(
                request, "Tài khoản không tồn tại. Vui lòng kiểm tra và thử lại!"
            )
            return redirect("forgotPassword")
    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Bây giờ bạn có thể đặt lại mật khẩu mới.")
        return redirect("resetPassword")
    else:
        messages.error(request, "Link này đã hết hạn. Vui lòng thực hiện lại!")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if len(password) < 6:
            messages.error(request, "Mật khẩu mới phải dài ít nhất 6 ký tự.")
            return redirect("resetPassword")

        if password == confirm_password:
            uid = request.session.get("uid")
            try:
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, "Mật khẩu đã được đặt lại thành công.")
                return redirect("login")
            except Account.DoesNotExist:
                messages.error(request, "Không tìm thấy người dùng.")
                return redirect("resetPassword")
        else:
            messages.error(request, "Hai mật khẩu bạn nhập không giống nhau!")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/reset_password.html")


@login_required(login_url="login")
def order_detail(request, order_id):
    # Lấy thông tin chi tiết đơn hàng và sản phẩm
    order_details = OrderDetail.objects.filter(order__order_number=order_id)
    order = get_object_or_404(Order, order_number=order_id)

    # Khởi tạo các giá trị tính toán
    subtotal = 0
    shipping_fee = 0
    grand_total = 0

    # Tính toán từng mục trong order_details
    for detail in order_details:
        detail.item_total = (
            detail.product_price * detail.quantity
        )  # Tổng tiền từng sản phẩm
        subtotal += detail.item_total  # Tổng tiền sản phẩm

        # Sắp xếp variations theo thứ tự "Color" trước, "Size" sau
        sorted_variations = detail.variations.all().order_by(
            Case(
                When(variation_category="Color", then=0),
                When(variation_category="Size", then=1),
                default=2,
            )
        )
        detail.sorted_variations = sorted_variations

    # Tính phí vận chuyển
    if subtotal <= 200000:
        shipping_fee = 25000

    # Tổng tiền phải trả
    grand_total = subtotal + shipping_fee

    # Định dạng tiền tệ (VNĐ)
    locale.setlocale(locale.LC_ALL, "vi_VN.UTF-8")
    formatted_subtotal = locale.format_string("%d", subtotal, grouping=True) + "đ"
    formatted_shipping_fee = (
        locale.format_string("%d", shipping_fee, grouping=True) + "đ"
    )
    formatted_grand_total = locale.format_string("%d", grand_total, grouping=True) + "đ"

    # Gửi dữ liệu vào context
    context = {
        "order_details": order_details,
        "order": order,
        "subtotal": formatted_subtotal,
        "shipping_fee": formatted_shipping_fee,
        "grand_total": formatted_grand_total,
    }
    return render(request, "accounts/order_detail.html", context)
