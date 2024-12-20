from django.shortcuts import render
from products.models import Product, ProductImage


def home(request):
    # Lấy 4 sản phẩm mới nhất với is_new=True
    new_products = Product.objects.filter(
        is_available=True,
        is_new=True
    ).order_by('-created_at')[:4]

    # Lấy 4 sản phẩm nổi bật với is_featured=True
    featured_products = Product.objects.filter(
        is_available=True,
        is_featured=True
    ).order_by('-created_at')[:4]

    # Kết hợp sản phẩm mới với ảnh chính (is_main=True)
    new_products_with_images = [
        {
            'product': product,
            'main_image': ProductImage.objects.filter(product=product, is_main=True).first()
        }
        for product in new_products
    ]

    # Kết hợp sản phẩm nổi bật với ảnh chính (is_main=True)
    featured_products_with_images = [
        {
            'product': product,
            'main_image': ProductImage.objects.filter(product=product, is_main=True).first()
        }
        for product in featured_products
    ]

    context = {
        'new_products_with_images': new_products_with_images,
        'featured_products_with_images': featured_products_with_images,
    }
    return render(request, 'home.html', context)
