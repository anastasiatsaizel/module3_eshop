from django.http import HttpResponse
from django.shortcuts import render
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

    context = {
        "products": products
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
    return render(request, "shop/register.html")


def logout_view(request):
    return render(request, "shop/logout.html")
