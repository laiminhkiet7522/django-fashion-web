from django.shortcuts import render, get_object_or_404
from products.models import Product, ProductImage
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.db.models import Q
from math import floor


def store(request, category_slug=None):
    categories = None
    products = None

    sort_by = request.GET.get("sort", "")  # Lấy tham số sort từ URL

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    # Thực hiện sắp xếp dựa trên tham số sort
    if sort_by == "price_high_to_low":
        products = products.order_by("-price")
    elif sort_by == "price_low_to_high":
        products = products.order_by("price")
    else:
        products = products.order_by("-created_at")

    product_count = products.count()

    # Kết hợp sản phẩm với ảnh
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

        # Tính phần trăm giảm giá
        discount_percentage = None
        if single_product.discount_price:
            discount_percentage = floor(
                (
                    (single_product.price - single_product.discount_price)
                    / single_product.price
                )
                * 100
            )

        # Sắp xếp danh sách size theo thứ tự cố định
        sizes_order = ["S", "M", "L", "XL"]
        sorted_sizes = sorted(
            single_product.variation_set.sizes(),
            key=lambda x: (
                sizes_order.index(x.variation_value)
                if x.variation_value in sizes_order
                else float("inf")
            ),
        )
    except Exception as e:
        raise e

    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "product_images": product_images,
        "discount_percentage": discount_percentage,
        "sorted_sizes": sorted_sizes,
    }

    return render(request, "store/product_detail.html", context)


def search(request):
    products = []
    product_count = 0
    keyword_exists = False
    sort_by = request.GET.get("sort", "")  # Lấy tham số sort từ URL

    if "keyword" in request.GET:
        keyword_exists = True
        keyword = request.GET["keyword"].strip()  # Loại bỏ khoảng trắng thừa
        if keyword:
            formatted_keyword = keyword.title()

            products = Product.objects.filter(
                Q(product_name__icontains=formatted_keyword)
            )

            # Thực hiện sắp xếp dựa trên tham số sort
            if sort_by == "price_high_to_low":
                products = products.order_by("-price")
            elif sort_by == "price_low_to_high":
                products = products.order_by("price")
            else:
                products = products.order_by("-created_at")

            product_count = products.count()

    # Kết hợp sản phẩm với ảnh
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
        "keyword": keyword if keyword_exists else "",
        "keyword_exists": keyword_exists,
    }
    return render(request, "store/store.html", context)
