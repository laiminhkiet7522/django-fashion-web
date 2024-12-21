from django.shortcuts import render
from products.models import Product, ProductImage


def store(request):
    # Lấy tất cả sản phẩm có sẵn
    all_products = Product.objects.filter(
        is_available=True).order_by('-created_at')

    # Đếm số sản phẩm được tìm thấy
    product_count = all_products.count()

    # Kết hợp sản phẩm với ảnh chính (is_main=True) và ảnh ngay sau ảnh chính
    products_with_images = [
        {
            'product': product,
            'main_image': ProductImage.objects.filter(product=product, is_main=True).first(),
            'next_image': ProductImage.objects.filter(product=product, is_main=False).order_by('id').first()
        }
        for product in all_products
    ]

    context = {
        'products_with_images': products_with_images,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)
