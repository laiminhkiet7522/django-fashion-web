from django.shortcuts import render, get_object_or_404
from products.models import Product, ProductImage
from category.models import Category


def store(request, category_slug=None):
    # Khởi tạo biến sản phẩm và danh mục
    categories = None
    products = None

    if category_slug:
        # Lấy danh mục theo slug, nếu không tìm thấy sẽ trả về lỗi 404
        categories = get_object_or_404(Category, slug=category_slug)
        # Lọc sản phẩm theo danh mục
        products = Product.objects.filter(
            category=categories, is_available=True).order_by('-created_at')
    else:
        # Lấy tất cả sản phẩm nếu không có category_slug
        products = Product.objects.filter(
            is_available=True).order_by('-created_at')

    # Đếm số sản phẩm được tìm thấy
    product_count = products.count()

    # Kết hợp sản phẩm với ảnh chính (is_main=True) và ảnh tiếp theo
    products_with_images = [
        {
            'product': product,
            'main_image': ProductImage.objects.filter(product=product, is_main=True).first(),
            'next_image': ProductImage.objects.filter(product=product, is_main=False).order_by('id').first()
        }
        for product in products
    ]

    context = {
        'products_with_images': products_with_images,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):

    return render(request, 'store/product_detail.html')
