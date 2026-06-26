from django.db import models
from django.contrib.auth.models import User
import os


def product_image_path(instance, filename):
    """Путь для загрузки изображений"""
    ext = filename.split('.')[-1]
    if instance.id:
        return f'products/product_{instance.id}.{ext}'
    return f'products/temp_{filename}'


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0

    def reviews_count(self):
        return self.reviews.count()

    def save(self, *args, **kwargs):
        """Переопределяем save для правильного переименования изображений"""
        # Проверяем, есть ли изображение и это новый объект
        is_new = self.pk is None
        image_file = self.image if not is_new else None

        # Сохраняем объект
        super().save(*args, **kwargs)

        # Если у нас есть изображение и это новый объект
        if is_new and self.image:
            old_path = self.image.path
            ext = old_path.split('.')[-1]
            new_filename = f'products/product_{self.id}.{ext}'
            new_path = os.path.join(os.path.dirname(old_path), new_filename)

            # Переименовываем файл
            if os.path.exists(old_path) and old_path != new_path:
                os.rename(old_path, new_path)
                # Обновляем имя в базе данных
                self.image.name = new_filename
                Product.objects.filter(id=self.id).update(image=new_filename)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']