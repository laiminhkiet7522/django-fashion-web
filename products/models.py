from django.db import models
from category.models import Category
from django.utils.text import slugify
from unidecode import unidecode
from ckeditor.fields import RichTextField
import os


class Product(models.Model):
    product_code = models.CharField(max_length=20, unique=True)  # Mã sản phẩm
    product_name = models.CharField(
        max_length=200, unique=True)  # Tên sản phẩm
    slug = models.SlugField(max_length=200, unique=True,
                            blank=True)  # Slug tự động tạo
    short_description = models.TextField(
        max_length=500, blank=True)  # Mô tả sản phẩm ngắn
    # Mô tả sản phẩm dài với CKEditor
    long_description = RichTextField(blank=True)
    price = models.PositiveIntegerField()  # Giá tiền (lưu số nguyên)
    discount_price = models.PositiveIntegerField(
        blank=True, null=True)  # Giá giảm (nếu có)
    currency = models.CharField(max_length=3, default="VND")  # Đơn vị tiền tệ
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
        if not self.pk or Product.objects.get(pk=self.pk).product_name != self.product_name:
            self.slug = slugify(unidecode(self.product_name))
        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Xóa tất cả ảnh liên quan khi xóa sản phẩm
        for image in self.images.all():
            image.delete()
        super(Product, self).delete(*args, **kwargs)

    def formatted_price(self):
        """Định dạng giá gốc (price) theo tiền Việt Nam"""
        return f"{self.price:,}đ".replace(",", ".")

    def formatted_discount_price(self):
        """Định dạng giá giảm (discount_price) theo tiền Việt Nam, nếu có"""
        if self.discount_price:
            return f"{self.discount_price:,}đ".replace(",", ".")
        return None

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)  # Liên kết với Product
    image = models.ImageField(
        upload_to='photos/products/')  # Đường dẫn upload ảnh
    is_main = models.BooleanField(default=False)  # Ảnh chính của sản phẩm

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = ProductImage.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.image != self.image:
                old_path = old_instance.image.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
        super(ProductImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Xóa file vật lý khi xóa ProductImage
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(ProductImage, self).delete(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.product_name}"
