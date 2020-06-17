from django.contrib.auth.models import User

from store.models import Product, Category, Cart, Buyer, Order
from store.serializers import ProductSerializer, CategorySerializer, CartSerializer, OrderSerializer
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from store.helpers import approve_session

from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'exists', 'title', 'price']


class CategoryViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CartViewSet(viewsets.ViewSet):

    @approve_session
    def list(self, request):
        session_key = request.META['HTTP_SESSION_KEY']
        cart = get_object_or_404(Cart, session_key=session_key)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        cart = Cart.create()
        serializer = CartSerializer(cart)
        return Response(serializer.data, 201)

    @action(detail=False, methods=['post'])
    def update_items(self, request):
        session_key = request.META.get('HTTP_SESSION_KEY')
        if session_key:
            cart = get_object_or_404(Cart, session_key=session_key)
            if len(Order.objects.filter(cart=cart)) is 0:
                cart.update_items(request.data)
                serializer = CartSerializer(cart)
                return Response(serializer.data, 201)
            else:
                return Response({"error": "this cart is already ordered"}, 403)
        else:
            return Response({"error": "header not specified"}, 400)


class OrderViewSet(viewsets.ViewSet):

    @approve_session
    def list(self, request):
        session_key = request.META['HTTP_SESSION_KEY']
        order = get_object_or_404(Order, cart__session_key=session_key)
        serializer = OrderSerializer(order)
        return Response(serializer.data, 200)

    @approve_session
    def create(self, request):
        session_key = request.META['HTTP_SESSION_KEY']
        cart = get_object_or_404(Cart, session_key=session_key)
        data = request.data
        buyer = Buyer(name=data['name'], surname=data['surname'], email=data['email'], phone=data['phone'],
                      address=data['address'])
        buyer.save()

        order = Order(cart=cart, buyer=buyer)
        order.save()

        # get all staff that have email
        staff = User.objects.filter(is_staff=True).exclude(email__exact='')

        emails = [user.email for user in staff]

        send_mail("New order", "New order from {} {}. Check it out in admin panel.\n Order id: {}"
                  .format(buyer.name, buyer.surname, order.id), settings.EMAIL_HOST_USER, emails)

        serializer = OrderSerializer(order)
        return Response(serializer.data, 201)
