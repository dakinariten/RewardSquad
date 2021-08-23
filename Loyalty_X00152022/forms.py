from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Store, StoreUser, User, UserDetails, RewardPoints, Product


# Forms for editing user profile


# Forms for Registration
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']


class UserRegistrationDetails(ModelForm):

    class Meta:
        model = UserDetails
        fields = ["contact_no", "dob"]


class ChooseStoreForm(ModelForm):
    store_name = forms.ModelChoiceField(queryset=Store.objects.all().order_by('store_name'))

    class Meta:
        model = Store
        fields = ['store_name']


class StoreUserAccountDetailsForm(ModelForm):

    class Meta:
        model = StoreUser
        fields = ['online_uid']


class UserAccountDetailsForm(ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UserDetailsAccountDetailsForm(ModelForm):

    class Meta:
        model = UserDetails
        fields = ['contact_no', 'dob', 'address', 'store_selection']


class PaymentPreparationForm(ModelForm):
    payment_choices = [('InStore', 'Pay in Store'), ('Paypal', 'Pay with Paypal')]
    payment = forms.CharField(widget=forms.RadioSelect(choices=payment_choices))

    class Meta:
        model = RewardPoints
        fields = ['total_points_earned', 'total_points_spent', 'payment']


class RewardPoints(forms.Form):
    reward_points_choices = (
        ('Redeem Points', 'Redeem Points'),
        ('Give Points', 'Give Points'),
        ('Points from Sale', 'Points from Sale')
    )
    points_amount = forms.DecimalField()
    user_id = forms.IntegerField()
    points_earned = forms.CharField(widget=forms.Select(choices=reward_points_choices), initial='Points from Sale')


class ProductForm(ModelForm):
    product_code = forms.CharField(max_length=50, required=False)
    ean_barcode = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Product
        fields = ['product_code', 'ean_barcode']
