from rest_framework import serializers
from .models import Product, ProductImage, Category, CartItem, Cart, Buyer, Order


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'photo']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'exists', 'category', 'images']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'price', 'session_key', 'items']


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer(many=False)
    cart = CartSerializer(many=False)

    class Meta:
        model = Order
        fields = '__all__'
