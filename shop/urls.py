from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout_view'),
    path('search/', views.search_product, name='search_product'),
    path('product/<int:pk>/add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='delete_product'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/remove/<int:pk>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/clear/', views.ClearCartView.as_view(), name='clear_cart'),
    path('cart/update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my_orders'),
]