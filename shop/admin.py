from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Purchase


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['id']


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "category", "created_at")
    search_fields = ("title", "description")
    list_filter = ("category", "created_at")
    list_editable = ['price', 'is_available'] if hasattr(Product, 'is_available') else ['price']


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    search_fields = ['user__username', 'user__email']


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity']
    search_fields = ['product__title', 'cart__user__username']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['id', 'user__username', 'user__email']
    ordering = ['-created_at']
    inlines = [OrderItemInline]

    @admin.display(description='Total Price (Kč)')
    def get_total_price(self, obj):
        # Вычисляем сумму через связанные элементы заказа
        return sum(item.price * item.quantity for item in obj.orderitem_set.all())


# Регистрируем модели
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Purchase)