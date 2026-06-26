from django.contrib import admin
from .models import Product, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'average_rating', 'reviews_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')

    def average_rating(self, obj):
        return f"{obj.average_rating():.1f}★"

    average_rating.short_description = "Рейтинг"

    def reviews_count(self, obj):
        return obj.reviews_count()

    reviews_count.short_description = "Кол-во отзывов"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'comment_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = "Комментарий"