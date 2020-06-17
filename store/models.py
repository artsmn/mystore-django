from django.db import models
import secrets


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    price = models.IntegerField(null=True)
    exists = models.BooleanField(default=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    photo = models.ImageField(upload_to="product_images/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.photo.url


class Buyer(models.Model):
    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=128)
    address = models.CharField(max_length=256)

    def __str__(self):
        return "{} {}".format(self.name, self.surname)


class Cart(models.Model):
    price = models.IntegerField()
    session_key = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.price = self.calc_price()
        super(Cart, self).save(*args, **kwargs)

    @classmethod
    def create(cls):
        session_key = secrets.token_hex(16)
        cart = cls(session_key=session_key, price=0)
        cart.save()
        return cart

    def update_items(self, data):
        if isinstance(data, list):
            self.items.all().delete()
            for item in data:
                product = Product.objects.get(id=item['product_id'])
                cart_item = CartItem(cart=self, quantity=item['quantity'], product=product)
                cart_item.save()
                self.save()
        else:
            raise Exception("Data should be type of list.")

    def __str__(self):
        return "Cart {}".format(self.id)

    # calc price of cart
    def calc_price(self):
        items = CartItem.objects.filter(cart=self)
        price = 0
        for item in items:
            price += item.quantity * item.product.price
        return price


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

    def save(self, *args, **kwargs):
        super(CartItem, self).save(*args, **kwargs)
        self.cart.price = self.cart.calc_price()  # calculate cart price after saving CartItem instance
        self.cart.save()

    def __str__(self):
        return self.product.title


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Ordered by {} {}".format(self.buyer.name, self.buyer.surname)
