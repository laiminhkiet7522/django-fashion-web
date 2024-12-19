from django.db import models
from django.utils.text import slugify
from unidecode import unidecode


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(max_length=255, blank=True)
    category_image = models.ImageField(
        upload_to='photos/categories', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        # Kiểm tra xem category_name có thay đổi không
        if not self.pk or Category.objects.get(pk=self.pk).category_name != self.category_name:
            self.slug = slugify(unidecode(self.category_name))
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name
