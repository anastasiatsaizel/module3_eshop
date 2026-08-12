from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, CartItem, Cart, Order, OrderItem
from .forms import ProductForm, ProductModelForm, CustomUserCreationForm, LoginForm, AddToCartForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
# Create your views here.

context = {
    "username": "Anastasia",
    "city": "Prague"
}

products = [
    {
        "id": 1,
        "name": "Cement",
        "description": "High-quality Portland cement.",
        "price": 150,
        "in_stock": True,
    },
    {
        "id": 2,
        "name": "Bricks",
        "description": "Red ceramic bricks.",
        "price": 12,
        "in_stock": True,
    },
    {
        "id": 3,
        "name": "Paint",
        "description": "Interior wall paint.",
        "price": 420,
        "in_stock": True,
    },
]

from django.shortcuts import render

def index(request):
    context = {
        "username": "Anastasia",
    }

    return render(request, "shop/index.html", context)


def about(request):
    return render(request, "shop/about.html")


def contact(request):
    return render(request, "shop/contact.html")


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        "products": products,
        "categories" : categories,
    }

    return render(request, "shop/products.html", context)


def product_detail(request, pk):

    product = None

    for item in products:
        if item["id"] == pk:
            product = item
            break

    context = {
        "product": product
    }

    return render(request, "shop/product_detail.html", context)


def login_view(request):

    return render(request, "shop/login.html")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем нового пользователя в БД
            login(request, user)  # Автоматически авторизуем пользователя
            # создаёт нового пользователя
            return redirect("index")  # редирект после регистрации
    else:
        form = CustomUserCreationForm()
    return render(request, "shop/register.html", {"form": form})


def logout_view(request):
    return render(request, "shop/logout.html")


def search_product(request):
    context = {}

    if request.method == 'POST':
        query = request.POST.get('search', '')
        context['message'] = f"You searched for: {query}"
    else:
        query = request.GET.get('search', '')
        if query:
            context['products'] = Product.objects.filter(title__icontains=query)
        else:
            context['products'] = Product.objects.all()

    return render(request, 'shop/search_product.html', context)


def add_product(request):
    success_message = None

    if request.method == 'POST':
        # загрузил ли пользователь данные или просто зашел на страницу
        form = ProductForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            success_message = f"Form successfully validated! Received: {cleaned_data['title']}"
    #         валидация данных правильно ли введены
    else:
        form = ProductForm()
    #     форма пустая

    context = {
        'form': form,
        'success_message': success_message
    }
    return render(request, 'shop/add_product.html', context)


def add_product_model(request):
    if request.method == 'POST':
        form = ProductModelForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductModelForm()

    return render(request, 'shop/add_product.html', {'form': form})


def edit_product(request, pk):
    # 1. Получаем товар по первичномусду ключу (pk) или отдаем страницу 404
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # 2. Связываем форму с новыми данными И старым объектом
        form = ProductModelForm(request.POST, instance=product)
        if form.is_valid():
            form.save() # Сохраняем изменения в существующий товар
            return redirect('product_list') # Перенаправляем на список товаров
    else:
        # 3. При GET-запросе передаем объект в instance, чтобы заполнить форму
        form = ProductModelForm(instance=product)

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'shop/edit_product.html', context)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)  # сохраняем пользователя в сессии
            return redirect("index")  # редирект после логина
    else:
        form = LoginForm()
    return render(request, "shop/login.html", {"form": form})


@login_required
def profile_view(request):
    return render(request, 'profile.html')


@login_required
def cart_view(request):
    # получаем корзину этого пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)
    # достаем товары iz этой корзины
    cart_items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/cart.html', context)


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required
def add_to_cart_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Получаем количество из POST запроса (по умолчанию 1)
        quantity_val = int(request.POST.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0}
        )

        total_quantity = cart_item.quantity + quantity_val

        # Проверка лимита в 10 штук
        if total_quantity > 10:
            # Можно перенаправить в корзину с сообщением или на детали товара
            return render(request, 'shop/product_detail.html', {
                'product': product,
                'form': AddToCartForm(initial={'quantity': quantity_val}),
                'error_message': f'Cannot add more than 10 units. You already have {cart_item.quantity} in cart.'
            })

        cart_item.quantity = total_quantity
        cart_item.save()
        return redirect('cart')


@login_required
def checkout_view(request):
    # получаем корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # если корзина пуста перенаправляем обратно в корзину
    if not cart_items.exists():
        return redirect('cart')

    # считаем итоговую стоимость
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        # Используем транзакцию для безопасности данных
        with transaction.atomic():
            # 1. Создаём новый объект Order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price
            )

            # 2. Копируем все CartItem в OrderItem (с сохранением цены на момент покупки)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # 3. Очищаем корзину пользователя
            cart_items.delete()

        # 4. Показываем страницу подтверждения
        return render(request, 'shop/order_success.html', {'order': order})

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set', 'orderitem_set__product').order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'shop/my_orders.html', context)