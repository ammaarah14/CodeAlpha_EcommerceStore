from django.contrib import admin
from django.urls import path, include
from products.views import (
    home,
    product_detail,
    add_to_cart,
    cart,
    update_cart,
    remove_from_cart,
    checkout,
    order_success,
    past_orders,
    wishlist,
    add_to_wishlist,
    remove_from_wishlist,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", cart, name="cart"),
    
    path(
        "cart/update/<int:product_id>/<str:action>/",
        update_cart,
        name="update_cart"
    ),
    
    path(
        "cart/remove/<int:product_id>/",
        remove_from_cart,
        name="remove_from_cart"
    ),
    
    path("checkout/", checkout, name="checkout"),
    
    path(
        "order-success/<int:order_id>/",
        order_success,
        name="order_success"
    ),
    
    path("orders/", past_orders, name="past_orders"),
    
    path("wishlist/", wishlist, name="wishlist"),
    
    path(
        "wishlist/add/<int:product_id>/",
        add_to_wishlist,
        name="add_to_wishlist"
    ),

    path(
        "wishlist/remove/<int:product_id>/",
        remove_from_wishlist,
        name="remove_from_wishlist"
    ),
    
    path("accounts/", include("accounts.urls")),
]
