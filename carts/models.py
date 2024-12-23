from django.db import models
from products.models import Product

# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        """Tính tổng tạm thời dựa trên giá giảm nếu có"""
        price = (
            self.product.discount_price
            if self.product.discount_price
            else self.product.price
        )
        return price * self.quantity

    def formatted_sub_total(self):
        """Định dạng lại giá tạm tính theo tiền Việt Nam"""
        price = (
            self.product.discount_price
            if self.product.discount_price
            else self.product.price
        )
        return f"{price * self.quantity:,}đ".replace(",", ".")
