from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout_view'),
    path('search/', views.search_product, name='search_product'),
    path('add_product/', views.add_product_model, name='add_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('product/<int:pk>/add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
]