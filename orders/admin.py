from django.contrib import admin
from .models import Payment, Order, OrderDetail

# Register your models here.


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    readonly_fields = (
        "payment",
        "user",
        "product",
        "quantity",
        "product_price",
        "ordered",
    )
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "full_name",
        "phone_number",
        "email",
        "shipping_fee",
        "order_total",
        "status",
        "is_ordered",
        "created_at",
    ]
    list_filter = ["status", "is_ordered"]
    search_fields = ["order_number", "first_name", "last_name", "phone_number", "email"]
    list_per_page = 20
    inlines = [OrderDetailInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail)
admin.site.register(Payment)
