from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Store, StoreUser, RewardPoints, UserDetails, Order, Offers, Product, OrderBasket, StoreOnlineRp

# Import all necessary models; SimpleHistoryAdmin keeps transaction records
# Change default display of Admin menu for models; make it more user friendly


class StoreAdmin(SimpleHistoryAdmin):
    search_fields = ['id', 'store_name', 'address', 'email', 'contact_no', 'group_id']
    list_display = ['store_name', 'address', 'email', 'contact_no', 'group_id', 'logo_url', 'id']
    list_filter = ['group_id']


class StoreUserAdmin(SimpleHistoryAdmin):
    list_display = ['user_type', 'username', 'store_name', 'online_uid']
    search_fields = ['user_type', 'username', 'store_name', 'online_uid']
    list_filter = ['store_id', 'user_type']

    def username(self, obj):
        return obj.user.username

    def store_name(self, obj):
        return obj.store.store_name


class OrderBasketAdmin(SimpleHistoryAdmin):
    list_display = ['order_id', 'username', 'product_code_id', 'offer', 'quantity']
    search_fields = ['order_id', 'username']

    def username(self, obj):
        return obj.user.username

    def offer(self, obj):
        return obj.offers.offer_title


class ProductAdmin(SimpleHistoryAdmin):
    list_display = ['product_code', 'product_title', 'price', 'ean_barcode', 'store_id', 'online_pid']
    search_fields = ['product_code', 'product_title', 'price', 'ean_barcode', 'store_id', 'online_pid']
    list_filter = ['price']


class OffersAdmin(SimpleHistoryAdmin):
    list_display = ['offer_title', 'store_id', 'price', 'date_start', 'date_end']
    search_fields = ['store_id', 'offer_title', 'price', 'date_start', 'date_end']
    list_filter = ['date_start', 'date_end']


class RewardPointsAdmin(SimpleHistoryAdmin):
    list_display = ['username', 'store_name', 'current_balance', 'last_update']
    search_fields = ['username', 'store_name']
    list_filter = ['user_id']

    def username(self, obj):
        return obj.user.username

    def store_name(self, obj):
        return obj.store.store_name


class OrderAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'order_total', 'order_status', 'username']
    list_filter = ['order_status']

    def username(self, obj):
        return obj.user.username


class StoreOnlineRpAdmin(SimpleHistoryAdmin):
    list_display = ['store_id', 'database_name', 'ecommerce_site_type']
    list_filter = ['ecommerce_site_type']


class UserDetailsAdmin(SimpleHistoryAdmin):
    list_display = ['username', 'contact_no', 'dob', 'store_selection_id']
    list_filter = ['store_selection_id']
    search_fields = ['username', 'store_selection_id']

    def username(self, obj):
        return obj.user.username


# Register your models here.
admin.site.register(Store, StoreAdmin)
admin.site.register(StoreOnlineRp, StoreOnlineRpAdmin)
admin.site.register(StoreUser, StoreUserAdmin)
admin.site.register(RewardPoints, RewardPointsAdmin)
admin.site.register(UserDetails, UserDetailsAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Offers, OffersAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OrderBasket, OrderBasketAdmin)