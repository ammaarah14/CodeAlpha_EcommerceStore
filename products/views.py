from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Order, OrderItem, WishlistItem


def home(request):
    products = Product.objects.all()

    return render(request, "home.html", {
        "products": products
    })


def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_product_ids = []

    if request.user.is_authenticated:

        wishlist_product_ids = list(
            WishlistItem.objects.filter(
                user=request.user
            ).values_list(
                "product_id",
                flat=True
            )
        )

    return render(request, "product_detail.html", {
        "product": product,
        "wishlist_product_ids": wishlist_product_ids
    })
    
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1
    else:
        return redirect("cart")

    request.session["cart"] = cart

    return redirect("cart")

def cart(request):
    cart = request.session.get("cart", {})

    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        subtotal = product.price * quantity
        total += subtotal

        products.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return render(request, "cart.html", {
        "products": products,
        "total": total
    })
    
def update_cart(request, product_id, action):

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id not in cart:
        return redirect("cart")

    product = get_object_or_404(Product, id=product_id)

    if action == "increase":

        if cart[product_id] < product.stock:
            cart[product_id] += 1
        else:
            messages.error(
                request,
                f"Only {product.stock} of {product.name} available."
            )

    elif action == "decrease":

        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session["cart"] = cart

    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart

    return redirect("cart")

@login_required
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    products = []
    total = 0

    # Check the cart before displaying checkout
    for product_id, quantity in cart.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        # Protect against invalid quantities
        if quantity <= 0:
            continue

        # Stock validation
        if quantity > product.stock:

            messages.error(
                request,
                f"Only {product.stock} of {product.name} "
                f"is currently available."
            )

            if product.stock == 0:
                del cart[product_id]
            else:
                cart[product_id] = product.stock

            request.session["cart"] = cart

            return redirect("cart")

        subtotal = product.price * quantity
        total += subtotal

        products.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    if not products:
        request.session["cart"] = {}
        return redirect("cart")

    if request.method == "POST":

        with transaction.atomic():

            # Check stock AGAIN immediately before creating the order
            for item in products:

                product = Product.objects.get(
                    id=item["product"].id
                )

                if item["quantity"] > product.stock:

                    messages.error(
                        request,
                        f"Sorry, {product.name} no longer has "
                        f"enough stock."
                    )

                    return redirect("cart")

            # Create the order only after ALL stock is valid
            order = Order.objects.create(
                user=request.user,
                total=total
            )

            for item in products:

                product = Product.objects.get(
                    id=item["product"].id
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"],
                    price=product.price
                )

                product.stock -= item["quantity"]
                product.save()

            request.session["cart"] = {}

        return redirect(
            "order_success",
            order_id=order.id
        )

    return render(request, "checkout.html", {
        "products": products,
        "total": total
    })

@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, "order_success.html", {
        "order": order
    })
    
@login_required
def past_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "past_orders.html", {
        "orders": orders
    })
    
@login_required
def wishlist(request):

    wishlist_items = WishlistItem.objects.filter(
        user=request.user
    ).select_related("product").order_by("-created_at")

    return render(request, "wishlist.html", {
        "wishlist_items": wishlist_items
    })
    
@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("product_detail", product_id=product.id)


@login_required
def remove_from_wishlist(request, product_id):

    WishlistItem.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect("wishlist")