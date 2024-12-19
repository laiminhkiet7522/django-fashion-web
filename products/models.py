from django.db import models
from category.models import Category
from django.utils.text import slugify
from unidecode import unidecode


class Product(models.Model):
    product_code = models.CharField(max_length=20, unique=True)  # Mã sản phẩm
    product_name = models.CharField(
        max_length=200, unique=True)  # Tên sản phẩm
    slug = models.SlugField(max_length=200, unique=True,
                            blank=True)  # Slug tự động tạo
    description = models.TextField(
        max_length=500, blank=True)  # Mô tả sản phẩm
    price = models.PositiveIntegerField()  # Giá tiền (lưu số nguyên)
    discount_price = models.PositiveIntegerField(
        blank=True, null=True)  # Giá giảm (nếu có)
    currency = models.CharField(max_length=3, default="VND")  # Đơn vị tiền tệ
    images = models.ImageField(upload_to='photos/products')  # Ảnh sản phẩm
    stock = models.PositiveIntegerField()  # Tồn kho
    is_available = models.BooleanField(default=True)  # Có sẵn hay không
    is_new = models.BooleanField(default=False)  # Sản phẩm mới hay không
    is_featured = models.BooleanField(
        default=False)  # Sản phẩm nổi bật hay không
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE)  # Liên kết với Category
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def save(self, *args, **kwargs):
        # Cập nhật slug khi product_name thay đổi hoặc là sản phẩm mới
        if not self.pk or Product.objects.get(pk=self.pk).product_name != self.product_name:
            self.slug = slugify(unidecode(self.product_name))
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    def formatted_price(self):
        # Trả về giá tiền được định dạng theo tiền Việt Nam
        return f"{self.price:,}đ".replace(",", ".")

    def formatted_discount_price(self):
        # Trả về giá giảm được định dạng theo tiền Việt Nam (nếu có)
        if self.discount_price:
            return f"{self.discount_price:,}đ".replace(",", ".")
        return None
