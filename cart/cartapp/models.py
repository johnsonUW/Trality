from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, connection
from django.db.models.signals import m2m_changed
from django.db.models import CharField, Q, F
from django.db.models.base import ModelBase
from django.dispatch import receiver
from django.utils.timezone import now


from decimal import Decimal
from functools import reduce
from operator import iand, ior

from django.db import models
from models import *

# Create your models here.

class Product(models.Model):

    """
    Container model for a product that stores information common to
    all of its variations such as the product's title and description.
    """

    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image_url = models.URLField(max_length=200)
    image = CharField(_("Image"), max_length=100, blank=True, null=True)
    categories = models.ManyToManyField("Category", blank=True, verbose_name=_("Product categories"))
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date_publish = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(_("Available for purchase"), default=False)

    orders = models.ManyToManyField('Order',through='LineItem', through_fields=('product', 'order'),)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")





@python_2_unicode_compatible
class ProductImage(Orderable):
    """
        An image for a product - a relationship is also defined with the
        product's variations so that each variation can potentially have
        it own image, while the relationship between the ``Product`` and
        ``ProductImage`` models ensures there is a single set of images
        for the product.
        """
    
    file = FileField(_("Image"), max_length=255, format="Image",
        upload_to=upload_to("shop.ProductImage.file", "product"))
        description = CharField(_("Description"), blank=True, max_length=100)
        product = models.ForeignKey("Product", related_name="images")
                     
        class Meta:
            verbose_name = _("Image")
            verbose_name_plural = _("Images")
            order_with_respect_to = "product"

    def __str__(self):
        value = self.description
            if not value:
                value = self.file.name
        if not value:
            value = ""
            return value


class Category(models.Model):
    """
        A category of products on the website.
    """

    featured_image = FileField(verbose_name=_("Featured Image"),
                           upload_to=upload_to("shop.Category.featured_image", "shop"),
                           format="Image", max_length=255, null=True, blank=True)
    products = models.ManyToManyField("Product", blank=True,
                    verbose_name=_("Products"),
                    through=Product.categories.through)
    sale = models.ForeignKey("Sale", verbose_name=_("Sale"), blank=True, null=True)

    class Meta:
        verbose_name = _("Product category")
        verbose_name_plural = _("Product categories")





class Cart(object):

    def __init__(self, *args, **kwargs):
        self.items = []
        self.total_price = 0

    def add_product(self, product):
        self.total_price += product.price

        for item in self.items:
            if item.product.id == product.id:
                item.quantity += 1
                return
        self.items.append(LineItem(product=product, unit_price=product.price, quantity=1))

class Order(models.Model):
    #name = models.CharField(max_length=50)
    #address = models.TextField()
    #email = models.EmailField()
billing_detail_first_name = CharField(_("First name"), max_length=100)
    billing_detail_last_name = CharField(_("Last name"), max_length=100)
    billing_detail_street = CharField(_("Street"), max_length=100)
    billing_detail_city = CharField(_("City/Suburb"), max_length=100)
    billing_detail_state = CharField(_("State/Region"), max_length=100)
    billing_detail_postcode = CharField(_("Zip/Postcode"), max_length=10)
    billing_detail_country = CharField(_("Country"), max_length=100)
    billing_detail_phone = CharField(_("Phone"), max_length=20)
    billing_detail_email = models.EmailField(_("Email"), max_length=254)
    shipping_detail_first_name = CharField(_("First name"), max_length=100)
    shipping_detail_last_name = CharField(_("Last name"), max_length=100)
    shipping_detail_street = CharField(_("Street"), max_length=100)
    shipping_detail_city = CharField(_("City/Suburb"), max_length=100)
    shipping_detail_state = CharField(_("State/Region"), max_length=100)
    shipping_detail_postcode = CharField(_("Zip/Postcode"), max_length=10)
    shipping_detail_country = CharField(_("Country"), max_length=100)
    shipping_detail_phone = CharField(_("Phone"), max_length=20)
    additional_instructions = models.TextField(_("Additional instructions"), blank=True)
    time = models.DateTimeField(_("Time"), auto_now_add=True, null=True)
    key = CharField(max_length=40, db_index=True)
    user_id = models.IntegerField(blank=True, null=True)
    tax_type = CharField(_("Tax type"), max_length=50, blank=True)
    tax_total = fields.MoneyField(_("Tax total"))
    item_total = fields.MoneyField(_("Item total"))
    discount_code = fields.DiscountCodeField(_("Discount code"), blank=True)
                                               discount_total = fields.MoneyField(_("Discount total"))
                                               total = fields.MoneyField(_("Order total"))
                                               transaction_id = CharField(_("Transaction ID"), max_length=255, null=True, blank=True)

    owner = models.ForeignKey('auth.User', related_name='order')

    class Meta:
    verbose_name = __("commercial meaning", "Order")
    verbose_name_plural = __("commercial meaning", "Orders")
    ordering = ("-id",)


    def __str__(self):
        return "#%s %s %s" % (self.id, self.billing_name(), self.time)
    
    def billing_name(self):
        return "%s %s" % (self.billing_detail_first_name, self.billing_detail_last_name)




class LineItem(models.Model):
    product = models.ForeignKey('Product')
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField()

@python_2_unicode_compatible
class Discount(models.Model):
    
    title = CharField(_("Title"), max_length=100)
    active = models.BooleanField(_("Active"), default=False)
    products = models.ManyToManyField("Product", blank=True,
                                      verbose_name=_("Products"))
    categories = models.ManyToManyField("Category", blank=True, related_name="%(class)s_related",
                    verbose_name=_("Categories"))
    discount_deduct = fields.MoneyField(_("Reduce by amount"))
    discount_percent = fields.PercentageField(_("Reduce by percent"), max_digits=5, decimal_places=2,
                            blank=True, null=True)
    discount_exact = fields.MoneyField(_("Reduce to amount"))
    valid_from = models.DateTimeField(_("Valid from"), blank=True, null=True)
    valid_to = models.DateTimeField(_("Valid to"), blank=True, null=True)
                                      
    class Meta:
        abstract = True
                                      
    def __str__(self):
        return self.title
    
    def all_products(self):
        """
            Return the selected products as well as the products in the
            selected categories.
            """
        filters = [category.filters() for category in self.categories.all()]
        filters = reduce(ior, filters + [Q(id__in=self.products.only("id"))])
        return Product.objects.filter(filters).distinct()

class Sale(Discount):
    """
        Stores sales field values for price and date range which when saved
        are then applied across products and variations according to the
        selected categories and products for the sale.
        """
    
    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")
    
    def save(self, *args, **kwargs):
        super(Sale, self).save(*args, **kwargs)
        self.update_products()
    
    def update_products(self):
        """
            Apply sales field value to products and variations according
            to the selected categories and products for the sale.
            """
       pass

    def delete(self, *args, **kwargs):
    """
        Clear this sale from products when deleting the sale.
        """
        self._clear()
        super(Sale, self).delete(*args, **kwargs)

    def _clear(self):
    """
        Clears previously applied sale field values from products prior
        to updating the sale, when deactivating it or deleting it.
        """
        update = {"sale_id": None, "sale_price": None,
                  "sale_from": None, "sale_to": None}
        for priced_model in (Product, ProductVariation):
            priced_model.objects.filter(sale_id=self.id).update(**update)

class DiscountCode(Discount):
    """
        A code that can be entered at the checkout process to have a
        discount applied to the total purchase amount.
        """
    
    code = fields.DiscountCodeField(_("Code"), unique=True)
    min_purchase = fields.MoneyField(_("Minimum total purchase"))
    free_shipping = models.BooleanField(_("Free shipping"), default=False)
    uses_remaining = models.IntegerField(_("Uses remaining"), blank=True, null=True, help_text=_("If you wish to limit the number of times a code may be used, set this value. It will be decremented upon each use."))
                                             
    objects = managers.DiscountCodeManager()
                                                                
    def calculate(self, amount):
        if self.discount_deduct is not None:
            if self.discount_deduct <= amount:
                return self.discount_deduct
        elif self.discount_percent is not None:
            return amount / Decimal("100") * self.discount_percent
        return 0
                                                                                            
class Meta:
    verbose_name = _("Discount code")
    verbose_name_plural = _("Discount codes")

