from django import forms
from models import *
import itertools

def anyTrue(predicate, sequence):
    return True in itertools.imap(predicate, sequence)
def endsWith(s, *endings):
    return anyTrue(s.endswith, endings)

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = []
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
    def clean_price(self):
        price = self.cleaned_data['price']
        if price<= 0:
            raise forms.ValidationError("price must be more than 0")
        return price
    def cleaned_image_url(self):
        url = self.cleaned_data['image_url']
        if not endsWith(url, '.jpg', 'png', '.gif'):
            raise forms.ValidationError('image must end with jpg, png, gif')
        return url

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = []
    def __init__(self, *args, **kwargs):
            super(OrderForm, self).__init__(*args, **kwargs)
