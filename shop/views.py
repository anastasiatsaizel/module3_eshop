from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, CartItem, Cart, Order, OrderItem
from .forms import ProductForm, ProductModelForm, CustomUserCreationForm, LoginForm, AddToCartForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.http import JsonResponse, HttpResponse
import resend
# Create your views here.


context = {
    "username": "Anastasia",
    "city": "Prague"
}


from django.shortcuts import render


class IndexView(TemplateView):
    template_name = "shop/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["username"] = self.request.user.username
        else:
            context["username"] = "Guest"

        context["company_name"] = "BuildMarket"
        return context


class AboutView(TemplateView):
    template_name = "shop/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_name"] = "BuildMarket"
        context["description"] = "Reliable building materials for your dream home."
        return context


class ContactView(TemplateView):
    template_name = "shop/contact.html"
    success_url = reverse_lazy('contact')  # Укажи имя твоего url-маршрута контактов

    resend.api_key = "re_3FtoCLhy_FSGg5gsLhDhDzZ5oe9WhjHFf"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_name"] = "BuildMarket"
        context["address"] = "Prague, Czech Republic"
        context["email"] = "info@buildmarket.cz"
        return context

    def post(self, request, *args, **kwargs):
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        user_message = request.POST.get('message')

        try:
            # Отправка через Resend
            resend.Emails.send({
                "from": "BuildMarket <onboarding@resend.dev>",
                "to": user_email,
                "subject": f"Welcome to BuildMarket, {user_name}!",
                "html": f"""
                    <h2>Hello, {user_name}!</h2>
                    <p>Thank you for reaching out to us.</p>
                    <p>We received your message:</p>
                    <blockquote style="background: #f9f9f9; padding: 10px; border-left: 3px solid #ccc;">
                        {user_message}
                    </blockquote>
                    <p>Our team will contact you shortly.</p>
                    <p>Best regards,<br><b>BuildMarket Team</b></p>
                """
            })

            messages.success(request, 'Thank you! A welcome email has been sent to your inbox.')

        except Exception as e:
            # Если возникнет ошибка — выведет понятное сообщение
            messages.error(request, f'Error sending email: {e}')

        return redirect(self.success_url)


class ProductListView(ListView):
    model = Product
    template_name = "shop/products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("search")
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset.order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AddToCartForm(initial={'quantity': 1})
        return context


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "shop/register.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        # сохраняем
        response = super().form_valid(form)
        # авторизуем нового пользователя после регистрации
        login(self.request, self.object)
        return response


class UserLoginView(LoginView):
    template_name = "shop/login.html"

    redirect_authenticated_user = True  # если хочу редиректить уже авторизованных

    def get_success_url(self):
        return reverse_lazy("index")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("index")


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


# mixin для проверки прав администратора
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)


class ProductCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductModelForm
    template_name = "shop/add_product.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        # валидация цены
        if form.cleaned_data["price"] <= 0:
            form.add_error("price", "Price must be greater than zero.")
            return self.form_invalid(form)
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductModelForm
    template_name = "shop/edit_product.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        if form.cleaned_data["price"] <= 0:
            form.add_error("price", "Price must be greater than zero.")
            return self.form_invalid(form)
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Product
    template_name = "shop/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")


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


class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = "shop/cart.html"
    context_object_name = "cart_items"

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        cart_items = self.get_queryset()
        context['cart'] = cart
        context['total_price'] = sum(item.product.price * item.quantity for item in cart_items)
        return context


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        quantity_val = int(request.POST.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0}
        )

        total_quantity = cart_item.quantity + quantity_val

        # превышение лимита в 10 штук??
        if total_quantity > 10:
            messages.error(
                request,
                f'Cannot add more than 10 units of "{product.title}". You already have {cart_item.quantity} in cart.'
            )
        else:
            cart_item.quantity = total_quantity
            cart_item.save()
            # успешное сообщение
            messages.success(request, f'Product "{product.title}" successfully added to cart! 🛒')

        # перенаправляем обратно на ту страницу с которой он отправил форму
        return redirect(request.META.get('HTTP_REFERER', 'product_list'))


class RemoveFromCartView(LoginRequiredMixin, DeleteView):
    model = CartItem
    success_url = reverse_lazy('cart')

    def get_queryset(self):
        # удаляем только из корзины нынешнего пользователя
        return CartItem.objects.filter(cart__user=self.request.user)


class ClearCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
        return redirect('cart')


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = cart.items.all() if cart else []

        if not cart_items.exists():
            messages.info(request, "Your cart is empty")
            return redirect('cart')

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        user_balance = getattr(request.user, 'balance', 0)

        return render(request, 'shop/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'user_balance': user_balance,
        })

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = cart.items.all() if cart else []

        if not cart_items.exists():
            messages.error(request, "Корзина пуста.")
            return redirect('cart')

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        user = request.user
        user_balance = getattr(user, 'balance', 0)

        # Проверка баланса
        if user_balance < total_price:
            messages.error(
                request,
                f'Insufficient funds on the balance! Total price: {total_price} Kč, your balance: {user_balance} Kč.'
            )
            return redirect('checkout')

        # Транзакция создания заказа
        with transaction.atomic():
            if hasattr(user, 'balance'):
                user.balance -= total_price
                user.save()

            # Создаем заказ только с полем user (и оставшимися стандартными полями вашей модели)
            order = Order.objects.create(
                user=user
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            cart_items.delete()

        messages.success(request, f'Order #{order.id} is successfully placed!')
        return render(request, 'shop/order_success.html', {'order': order})


class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)

        try:
            new_quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            new_quantity = 1

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()

            item_total = cart_item.product.price * cart_item.quantity

            if hasattr(cart_item, 'cart'):
                all_items = cart_item.cart.items.all()
            else:
                all_items = CartItem.objects.filter(user=request.user)

            cart_total = sum(i.product.price * i.quantity for i in all_items)

            return JsonResponse({
                'success': True,
                'item_total': f"{item_total:.2f}",
                'cart_total': f"{cart_total:.2f}"
            })

        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shop/my_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items', 'items__product'
        ).order_by('-created_at')


