import mongoengine as me
import datetime
from typing import Tuple
me.connect('SHOP_DB')


class Customer(me.Document):
    user_id = me.IntField(unique=True)
    username = me.StringField(min_length=1, max_length=256)
    phone_number = me.StringField(min_length=12)
    address = me.StringField()
    first_name = me.StringField(min_length=1, max_length=256)
    surname = me.StringField(min_length=1, max_length=256)
    age = me.IntField(min_value=12, max_value=99)

    def get_or_create_current_cart(self) -> Tuple[bool, 'Cart']:
        created = False
        cart = Cart.objects.filter(customer = self, is_archived = False).get()
        if  cart:
            return created, cart
        else:
            return created, Cart.objects.created(customer = self)





class Characteristics(me.EmbeddedDocument):
    height = me.DecimalField()
    width = me.DecimalField()
    weight = me.DecimalField()


class Category(me.Document):
    title = me.StringField(min_length=2, max_length=512, required=True)
    slug = me.StringField(min_length=2, max_length=512, unique=True, required=True)
    description = me.StringField(min_length=2, max_length=2048)
    subcategories = me.ListField(me.ReferenceField('self'))
    parent = me.ReferenceField('self')

    @classmethod
    def get_root(cls):
        return cls.objects(parent=None)

    def add_subcategory(self, subcategory_obj):
        subcategory_obj.parent = self
        self.subcategories.append(subcategory_obj.save())
        self.save()

    @property
    def products(self):
        return Product.objects(category=self)

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return not self.subcategories


class Product(me.Document):
    title = me.StringField(min_length=2, max_length=512, required=True)
    slug = me.StringField(min_length=2, max_length=512, unique=True, required=True)
    description = me.StringField(min_length=2, max_length=2048)
    characteristics = me.EmbeddedDocumentField(Characteristics)
    price = me.DecimalField(min_value=0, force_string=True, required=True)
    discount_percentage = me.IntField(min_value=0, max_value=100, default=0)
    category = me.ReferenceField(Category)
    image = me.FileField()

    @classmethod
    def get_discount_products(cls):
        return cls.objects(dicount_percentage__gt=0)

    def get_price(self):
        percentage = 100 - self.discount_percentage
        return self.price * percentage / 100

class CartItem(me.EmbeddedDocument):
    product = me.ReferenceField('Product')
    quantity = me.IntField(min_value = 1)

    @property
    def price(self):
        return self.product.get_price() * self.quantity

class Cart(me.Document):
    customer = me.ReferenceField(Customer)
    cart_items = me.EmbeddedDocumentListField(CartItem)
    is_archived = me.BooleanField(default = False)

    def add_item(self,item:CartItem):
        if item in self.cart_items:
            self.cart_items[self.cart_items.index(item)].quantity +=1
        else:
            self.cart_items.append(item)
        self.save()

    def archived(self):
        self.is_archived = True
        self.save()

class News(me.Document):
    title = me.StringField(min_length=2, max_length=512)
    body = me.StringField(min_length=10, max_length=4096)
    pub_date = me.DateTimeField(default=datetime.datetime.now)


class Texts(me.Document):
    choices = (
        ('Greeting', 'Greeting'),
        ('Buy', 'Buy')
    )
    text = me.StringField(choices=choices)