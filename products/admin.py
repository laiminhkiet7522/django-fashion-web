from django.contrib import admin
from .models import Product, ProductImage

# Inline model để quản lý ảnh liên quan


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Số lượng dòng trống mặc định để thêm ảnh mới
    fields = ('image', 'is_main')  # Các trường được hiển thị
    readonly_fields = ()  # Nếu có trường nào cần đặt chỉ đọc

# Tùy chỉnh admin cho Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'price', 'stock',
                    'category', 'updated_at', 'is_available', 'is_new', 'is_featured')

    readonly_fields = ('slug',)  # Slug là readonly

    list_editable = ('price', 'stock', 'is_available', 'is_new', 'is_featured')

    list_display_links = ('product_code', 'product_name')

    # Thêm inline vào trang chi tiết sản phẩm
    inlines = [ProductImageInline]


# Đăng ký các model vào admin
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
