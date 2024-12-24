from django.db import models
from category.models import Category
from django.utils.text import slugify
from unidecode import unidecode
from ckeditor.fields import RichTextField
from django.urls import reverse
import os
import random
import string


def generate_unique_image_name(instance, filename):
    """
    Sinh một tên file duy nhất cho hình ảnh dựa trên "image_" và chuỗi ngẫu nhiên 10 ký tự.
    """
    # Lấy phần mở rộng của file
    ext = os.path.splitext(filename)[-1].lower()
    # Tạo chuỗi ngẫu nhiên 10 ký tự
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    # Định dạng tên file
    new_filename = f"image_{random_string}{ext}"
    return os.path.join("photos/products/", new_filename)


class Product(models.Model):
    product_code = models.CharField(max_length=20, unique=True)  # Mã sản phẩm
    product_name = models.CharField(max_length=200, unique=True)  # Tên sản phẩm
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # Slug tự động tạo
    short_description = models.TextField(
        max_length=500, blank=True
    )  # Mô tả sản phẩm ngắn
    # Mô tả sản phẩm dài với CKEditor
    long_description = RichTextField(blank=True)
    price = models.PositiveIntegerField()  # Giá tiền (lưu số nguyên)
    discount_price = models.PositiveIntegerField(
        blank=True, null=True
    )  # Giá giảm (nếu có)
    currency = models.CharField(max_length=3, default="VND")  # Đơn vị tiền tệ
    stock = models.PositiveIntegerField()  # Tồn kho
    is_available = models.BooleanField(default=True)  # Có sẵn hay không
    is_new = models.BooleanField(default=False)  # Sản phẩm mới hay không
    is_featured = models.BooleanField(default=False)  # Sản phẩm nổi bật hay không
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE
    )  # Liên kết với Category
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        # Viết hoa chữ cái đầu của mỗi từ trong tên sản phẩm
        if self.product_name:
            self.product_name = self.product_name.title()

        if (
            not self.pk
            or Product.objects.get(pk=self.pk).product_name != self.product_name
        ):
            self.slug = slugify(unidecode(self.product_name))

        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Xóa tất cả ảnh liên quan khi xóa sản phẩm
        for image in self.images.all():
            image.delete()
        super(Product, self).delete(*args, **kwargs)

    def formatted_price(self):
        # Định dạng giá gốc (price) theo tiền Việt Nam
        return f"{self.price:,}đ".replace(",", ".")

    def formatted_discount_price(self):
        # Định dạng giá giảm (discount_price) theo tiền Việt Nam, nếu có
        if self.discount_price:
            return f"{self.discount_price:,}đ".replace(",", ".")
        return None

    def get_url(self):
        return reverse("product_detail", args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )  # Liên kết với Product
    image = models.ImageField(
        upload_to=generate_unique_image_name
    )  # Sử dụng hàm để sinh tên file
    is_main = models.BooleanField(default=False)  # Ảnh chính của sản phẩm

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

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


variation_category_choice = (
    ("color", "color"),
    ("size", "size"),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choice
    )
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.product
