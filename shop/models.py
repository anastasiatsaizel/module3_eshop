from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(blank=True, null=True, upload_to="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    # Связываем корзину с пользователем 1 к 1
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.user.username}"


class CartItem(models.Model):
    # Элемент корзины: связывает конкретную корзину и продукт
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="in_carts"
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        # Один и тот же товар не должен дублироваться отдельными строчками в одной корзине
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',
        verbose_name='Order')
    # Если удаляют главного, удаляй и всех, кто к нему привязан. в бд не останется дочерних записей при удалении Order
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name='Product'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Price for 1 piece')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ordered Item'
        verbose_name_plural = 'Ordered Items'

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"


class Purchase(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='purchase',
        verbose_name='Ordered Item')
    total_price = models.DecimalField(max_digits=12,
        decimal_places=2,
        editable=False, # Скрываем от редактирования в админке
        verbose_name='Total Price')
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name='Date of payment')

    class Meta:
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'

    def save(self, *args, **kwargs):
        # 1. Автоматический расчет суммы: цена * количество из OrderItem
        if self.order_item:
            self.total_amount = self.order_item.price * self.order_item.quantity
        else:
            raise ValidationError("Нельзя создать Покупку без привязанного OrderItem")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase #{self.id} — {self.total_price} Kč."

# [ User ] ──(1:1)──> [ Cart ] ──(1:N)──> [ CartItem ] <──(N:1)── [ Product ]
#    │                                                                 ▲
#    └──(1:N)───────> [ Order ] ──(1:N)─> [ OrderItem ] ──────────────┤
#                                              │
#                                            (1:1)
#                                              ▼
#                                         [ Purchase ]