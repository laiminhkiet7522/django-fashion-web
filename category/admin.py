from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug')
    readonly_fields = ('slug',)  # Hiển thị slug nhưng không chỉnh sửa


admin.site.register(Category, CategoryAdmin)
