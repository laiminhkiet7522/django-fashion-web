from django.shortcuts import render, get_object_or_404
from products.models import Product, ProductImage
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.db.models import Q


def store(request, category_slug=None):

    categories = None
    products = None

    if category_slug:
        # Lấy danh mục theo slug, nếu không tìm thấy sẽ trả về lỗi 404
        categories = get_object_or_404(Category, slug=category_slug)
        # Lọc sản phẩm theo danh mục
        products = Product.objects.filter(
            category=categories, is_available=True
        ).order_by("-created_at")
    else:
        # Lấy tất cả sản phẩm nếu không có category_slug
        products = Product.objects.filter(is_available=True).order_by("-created_at")

    # Đếm số sản phẩm được tìm thấy
    product_count = products.count()

    # Kết hợp sản phẩm với ảnh chính (is_main=True) và ảnh tiếp theo ảnh chính
    products_with_images = [
        {
            "product": product,
            "main_image": ProductImage.objects.filter(
                product=product, is_main=True
            ).first(),
            "next_image": ProductImage.objects.filter(product=product, is_main=False)
            .order_by("id")
            .first(),
        }
        for product in products
    ]

    context = {
        "products_with_images": products_with_images,
        "product_count": product_count,
        "category_slug": category_slug,
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):

    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()
        product_images = ProductImage.objects.filter(product=single_product).order_by(
            "-is_main", "id"
        )
    except Exception as e:
        raise e

    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "product_images": product_images,
    }

    return render(request, "store/product_detail.html", context)


def search(request):
    products = []
    product_count = 0
    keyword_exists = False

    if "keyword" in request.GET:
        keyword_exists = True
        keyword = request.GET["keyword"].strip()  # Loại bỏ khoảng trắng thừa
        if keyword:
            # Viết hoa chữ cái đầu mỗi từ
            formatted_keyword = keyword.title()

            # Sử dụng icontains để tìm kiếm không phân biệt chữ hoa, chữ thường
            products = Product.objects.order_by("-created_at").filter(
                Q(product_name__icontains=formatted_keyword)
            )
            product_count = products.count()

    # Kết hợp sản phẩm với ảnh chính (is_main=True) và ảnh tiếp theo ảnh chính
    products_with_images = [
        {
            "product": product,
            "main_image": ProductImage.objects.filter(
                product=product, is_main=True
            ).first(),
            "next_image": ProductImage.objects.filter(product=product, is_main=False)
            .order_by("id")
            .first(),
        }
        for product in products
    ]

    context = {
        "products_with_images": products_with_images,
        "product_count": product_count,
        "keyword": keyword,
        "keyword_exists": keyword_exists,
    }
    return render(request, "store/store.html", context)
