from .models import Category


def menu_links(request):
    # Lấy tất cả các danh mục
    links = Category.objects.all()

    # Gắn thêm các URL cụ thể cho từng danh mục
    specific_urls = {
        'shirt_url': Category.objects.filter(category_name='Áo sơ mi').first().get_url() if Category.objects.filter(category_name='Áo sơ mi').exists() else '#',
        'polo_url': Category.objects.filter(category_name='Áo Polo').first().get_url() if Category.objects.filter(category_name='Áo Polo').exists() else '#',
        'jacket_url': Category.objects.filter(category_name='Áo khoác').first().get_url() if Category.objects.filter(category_name='Áo khoác').exists() else '#',
    }

    # Trả về cả danh sách links và các URL cụ thể
    return dict(links=links, specific_urls=specific_urls)
