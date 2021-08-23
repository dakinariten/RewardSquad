from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [path('admin/', admin.site.urls), path('', views.index, name='admin'),
               path('account-details/', views.account_details, name='account_details'),
               path('accounts/', include('django.contrib.auth.urls')),
               path('adjust-points/', views.adjust_points, name='adjust_points'),
               path('ajax_posting/', views.ajax_posting, name='ajax_posting'),
               path('', views.index, name='index'),
               path('all-orders/', views.order_history_full, name="all-orders"),
               path('choose-store/', views.choose_store, name='choose-store'),
               path('contact/', views.contact, name='contact'),
               path('index/', views.index, name='index'),
               path('offers/', views.offers, name='offers'),
               path('order-history/', views.order_history, name='order-history'),
               path('payment/', views.payment, name="payment"),
               path('paypal/', include('paypal.standard.ipn.urls')),
               path("register/", views.register_view, name="register"),
               path('scan/', views.scan, name='scan'),
               path('shop/', views.shop, name='shop'),
               path('shop/checkout/', views.checkout, name='checkout'),
               path('shop/submit-product/', views.submit_product, name='submit_product'),
               path('support/', views.support, name='support'),
               path('user-management/', views.user_management, name='user-management')
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
