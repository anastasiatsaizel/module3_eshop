from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Purchase  # импортируем нашу модель

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['id']


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "category", "created_at")  # колонки, которые будут отображаться
    search_fields = ("title", "description")               # поле для поиска
    list_filter = ("category", "created_at")                # фильтр сбоку
    list_editable = ['price', 'is_available'] if hasattr(Product, 'is_available') else ['price']


class OrderAdmin(admin.ModelAdmin):
    # Основная информация по заказам
    list_display = ['id', 'user', 'status', 'total_price', 'created_at'] if hasattr(Order, 'total_price') else ['id',
                                                                                                                'user',
                                                                                                                'created_at']
    # Фильтрация по датам заказа
    list_filter = ['created_at']
    # Поиск по ID заказа, имени пользователя и его Email
    search_fields = ['id', 'user__username', 'user__email']
    ordering = ['-created_at']


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    search_fields = ['user__username', 'user__email']


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity']
    search_fields = ['product__title', 'cart__user__username']


# регистрируем модель
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Purchase)