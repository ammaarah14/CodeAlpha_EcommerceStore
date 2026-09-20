from django.contrib import admin
from .models import Product, Order, OrderItem, WishlistItem


admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "product__name",
    )