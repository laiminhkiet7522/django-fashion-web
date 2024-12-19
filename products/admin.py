from django.contrib import admin
from .models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'price', 'stock',
                    'category', 'updated_at', 'is_available', 'is_new', 'is_featured')
    
    # Đặt slug là readonly để không thể chỉnh sửa trực tiếp
    readonly_fields = ('slug',)

    # Có thể chỉnh sửa trực tiếp các trường này trong danh sách
    list_editable = ('price', 'stock', 'is_available', 'is_new', 'is_featured')

    # Chỉ định các trường được liên kết để dẫn đến trang chi tiết đối tượng.
    list_display_links = ('product_code', 'product_name')

admin.site.register(Product, ProductAdmin)
