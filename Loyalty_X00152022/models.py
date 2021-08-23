from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from simple_history.models import HistoricalRecords
import django.dispatch

# Create your models here.


class Store(models.Model):

    def __str__(self):
        return self.store_name

    store_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    contact_no = models.CharField(max_length=20)
    group_id = models.CharField(max_length=10, blank=True)
    website = models.URLField(blank=True)
    logo_url = models.ImageField(upload_to='Store')
    online_rp = models.BooleanField(default=False)
    rp_euro_ratio = models.DecimalField(default=0.01, blank=False, decimal_places=2, max_digits=10)
    history = HistoricalRecords()


class StoreOnlineRp(models.Model):
    def __str__(self):
        return self.database_name

    store = models.OneToOneField(Store, on_delete=models.CASCADE)
    database_name = models.CharField(max_length=100, blank=False)
    database_url = models.CharField(max_length=200, blank=False)
    database_type = models.CharField(max_length=50, blank=False, default="MySQL")
    ecommerce_site_type = models.CharField(max_length=50, blank=False)
    user_table_name = models.CharField(max_length=50, blank=False)
    user_id_column_name = models.CharField(max_length=50, blank=False)
    # Reward Points are not built into every ecom system, and several solutions exist
    # Not compulsory for this application, as it can be configured to take the user's spend
    # and add it to their reward points balance (for use in-store)
    rp_table_name = models.CharField(max_length=50, blank=True)
    rp_column_name = models.CharField(max_length=50, blank=True)


class StoreUser(models.Model):

    def __str__(self):
        return self.user.username
    # Define Choices for user_type
    CUSTOMER = "CUST"
    CLERK = "CLRK"
    MERCHANT = "MCHT"
    ADMIN = "ADMN"
    user_choices = [(CUSTOMER, "CUSTOMER"), (CLERK, "CLERK"), (MERCHANT, "MERCHANT"), (ADMIN, "ADMIN")]
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=4, choices=user_choices, default=CUSTOMER)
    online_uid = models.CharField(max_length=50, blank=True)
    rp_acc_link = models.BooleanField(default=False)


class RewardPoints(models.Model):

    def __str__(self):
        return self.user.username

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_points_earned = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=10)
    total_points_spent = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=10)
    total_points_given = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=10)
    current_balance = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=10)
    update_successful = models.BooleanField(default=True)
    last_update = models.DateTimeField(default=now)
    history = HistoricalRecords()


class UserDetails(models.Model):

    def __str__(self):
        return self.user.username

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_no = models.CharField(max_length=20)
    dob = models.DateField()
    address = models.CharField(max_length=255, blank=True)
    store_selection = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True)
    history = HistoricalRecords()


class Order(models.Model):

    def __str__(self):
        return self.order_status
    # Define order status for choices
    NOT_PLACED = "NOT PLACED"
    PLACED = "PLACED"
    PENDING = "PENDING"
    PAYPAL = "AWAITING PAYMENT"
    COMPLETE = "COMPLETE"
    MANUAL = "MANUAL CHECKOUT"
    CANCELLED = "CANCELLED"
    order_choices = [(NOT_PLACED, NOT_PLACED), (PLACED, PLACED), (PENDING, PENDING), (COMPLETE, COMPLETE),
                     (MANUAL, MANUAL), (PAYPAL, PAYPAL), (CANCELLED, CANCELLED)]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_total = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    date = models.DateTimeField(default=django.utils.timezone.now())
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=20, choices=order_choices, default=NOT_PLACED)
    history = HistoricalRecords()


class Product(models.Model):

    def __str__(self):
        return self.product_title

    product_code = models.CharField(max_length=50, blank=False)
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    product_title = models.CharField(max_length=200, blank=False)
    price = models.DecimalField(blank=False, default=0, decimal_places=2, max_digits=10)
    # EAN code can be blank as some products do not have them
    ean_barcode = models.CharField(max_length=50, blank=True)
    manufacturer = models.CharField(max_length=50, blank=False)
    # Link to the product ID of webstore (if applicable)
    online_pid = models.CharField(max_length=50, blank=True)
    history = HistoricalRecords()


class Offers(models.Model):
    def __str__(self):
        return self.offer_title

    offer_title = models.CharField(max_length=200, blank=False)
    # Displays at 64 char
    offer_text_short = models.CharField(max_length=64, blank=False)
    # Ideally this field should not be blank, however many companies will just want the title to do the job
    offer_text_long = models.CharField(max_length=1000, blank=True)
    image_url = models.ImageField(upload_to='Offers', blank=False)
    price = models.DecimalField(blank=False, default=0, decimal_places=2, max_digits=10)
    date_start = models.DateField(default=now(), blank=False)
    # Default the offer time period for 1 week
    date_end = models.DateField(default=now() + timedelta(days=7), blank=False)
    # User here refers to user whom created the offer
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    history = HistoricalRecords()


class OrderBasket(models.Model):
    def __str__(self):
        return str(self.user.username)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Use Django's PK for Product; access product code through the Product Model
    # Optional for use with Offers
    product_code = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, default=1)
    # Optional for use with regular products
    offer = models.ForeignKey(Offers, on_delete=models.CASCADE, blank=True, null=True)
