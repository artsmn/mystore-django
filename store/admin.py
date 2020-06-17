from django.contrib import admin
from .models import Product, ProductImage, Category, Cart, CartItem, Order, Buyer


class CartItemInline(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]


# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Buyer)



