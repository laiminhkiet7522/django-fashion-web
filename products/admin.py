from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Product, ProductImage

# Inline model để quản lý ảnh liên quan


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Số lượng dòng trống mặc định để thêm ảnh mới
    fields = ('image', 'is_main')  # Các trường được hiển thị
    readonly_fields = ()  # Nếu có trường nào cần đặt chỉ đọc

# Tùy chỉnh form để sử dụng CKEditor cho long_description


class ProductAdminForm(forms.ModelForm):
    long_description = forms.CharField(
        widget=CKEditorWidget())  # Tích hợp CKEditor

    class Meta:
        model = Product
        fields = '__all__'

# Tùy chỉnh admin cho Product


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm  # Sử dụng form tùy chỉnh
    list_display = ('product_code', 'product_name', 'price', 'discount_price',
                    'category', 'updated_at', 'is_available', 'is_new', 'is_featured')
    readonly_fields = ('slug',)  # Slug là readonly
    list_editable = ('price', 'discount_price',
                     'is_available', 'is_new', 'is_featured')
    list_display_links = ('product_code', 'product_name')
    inlines = [ProductImageInline]  # Thêm inline quản lý ảnh


# Đăng ký các model vào admin
admin.site.register(Product, ProductAdmin)
