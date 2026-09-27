from django import forms
from .models import Category, Product
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm

class ProductForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label="Product Title"
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Price"
    )
    category = forms.ChoiceField(
        label="Category",
        choices=[]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [
            (c.id, c.name) for c in Category.objects.all()
        ]


class ProductModelForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'price', 'category']

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter product title...'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }

        error_messages = {
            'price': {
                'required': 'Please specify the price.',
            }
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 1:
            raise forms.ValidationError("Price cannot be less than 1.")
        return price

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        forbidden_words = ['запрещено', 'forbidden', 'spam']

        for word in forbidden_words:
            if word in title.lower():
                raise forms.ValidationError(
                    f"Product title contains forbidden word: '{word}'."
                )
        return title


User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Wrong username or password.")
        return cleaned_data


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        label="Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20})
    )
    product = forms.IntegerField(widget=forms.HiddenInput(), required=False)