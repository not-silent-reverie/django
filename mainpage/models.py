from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os


def product_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if instance.id:
        return f'products/product_{instance.id}.{ext}'
    return f'products/temp_{filename}'


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Категория"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Старая цена"
    )
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        null=True,
        verbose_name="Изображение",
        default='products/default.jpg'
    )
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0

    def reviews_count(self):
        return self.reviews.count()

    def is_on_sale(self):
        return self.old_price is not None and self.old_price > self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.slug:
            self.slug = slugify(self.name)

            is_new = self.pk is None
            super().save(*args, **kwargs)

            if is_new and self.image and self.image.name:
                old_path = self.image.path
                ext = old_path.split('.')[-1]
                new_filename = f'products/product_{self.id}.{ext}'
                new_path = os.path.join(os.path.dirname(old_path), new_filename)

                if os.path.exists(old_path) and old_path != new_path:
                    os.rename(old_path, new_path)
                    self.image.name = new_filename
                    Product.objects.filter(id=self.id).update(image=new_filename)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Товар"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name="Оценка"
    )
    comment = models.TextField(verbose_name="Комментарий")
    is_verified = models.BooleanField(default=False, verbose_name="Подтверждённый отзыв")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}⭐"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        unique_together = ['product', 'user']

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    bio = models.TextField(blank=True, verbose_name="О себе")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"