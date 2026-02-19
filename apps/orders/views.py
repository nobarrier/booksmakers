from django.shortcuts import render, redirect
from .models import Order, OrderItem
from apps.catalog.models import Product


def checkout(request):
    cart = request.session.get("cart", {})

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        total_price = 0
        order = Order.objects.create(
            name=name, phone=phone, address=address, total_price=0
        )

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            price = product.price * quantity
            total_price += price

            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=price
            )

        order.total_price = total_price
        order.save()

        request.session["cart"] = {}

        return redirect("orders:complete")

    return render(request, "orders/checkout.html")


def complete(request):
    return render(request, "orders/complete.html")
