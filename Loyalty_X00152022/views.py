import datetime
import decimal
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import qrcode
import qrcode.image.svg
from io import BytesIO
from django import forms
from . import forms
from django.contrib.auth import login
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import RewardPoints
from . import models
import Loyalty_X00152022.rp as rp

"""
Any template extending base.html requires the following attributes in a dict (context)

context['store'] = models.Store.objects.get(id=models.UserDetails.objects.get
                                                (user_id=request.user.id).store_selection_id)
context['icon_type'] = models.StoreUser.objects.get(user_id=request.user.id,store_id=models.UserDetails.objects.get
                                                (user_id=request.user.id).store_selection_id)

"""


@login_required()
def index(request):
    template = loader.get_template('Loyalty_X00152022/index.html')
    # Get prerequisite info for base.html
    context = rp.get_store_selection(request)
    # QR Code Generator
    img = qrcode.make(request.user.id, image_factory=qrcode.image.svg.SvgImage, box_size=20)
    stream = BytesIO()
    img.save(stream)
    # Points Balance
    try:
        selected_store = models.UserDetails.objects.get(user_id=request.user.id)
        rp.check_balance(user_id=request.user.id, store_id=selected_store.store_selection_id)
        points = RewardPoints.objects.get(user_id=request.user.id, store_id=selected_store.store_selection_id)
        context["balance"] = points
    except RewardPoints.DoesNotExist:
        return redirect('account_details')
    context["svg"] = stream.getvalue().decode()
    context["user"] = request.user
    context["forms"] = forms
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get('id') == "order-history":
            order_list = models.Order.objects.filter(user_id=request.user.id,
                                                     store_id=models.UserDetails.objects.get
                                                     (user_id=request.user.id).store_selection_id).order_by('-date')
            order_list_display = []
            for item in order_list:
                temp = {"OrderID": item.id, "Amount": item.order_total, "Date": item.date.date(),
                        "Status": item.order_status}
                if item.order_status == "PENDING":
                    temp["Action"] = "<button name='pay-order' value='"+str(item.id)+"' type='submit'>" \
                                                                                     "<span class='material-icons'>" \
                                                                                     "paid</span></button>" \
                                                                                     "<button name='view-order' " \
                                                                                     "value='" \
                                     + str(item.id) + "' type='submit'><span class='material-icons'>" \
                                                                                           "receipt</span></button>"
                else:
                    temp["Action"] = "<button name='pay-order' value='"+str(item.id) + "' type='submit' " \
                                                                                      "disabled " \
                                                                                      "style='visibility: hidden;'>" \
                                                                                      "<span class='material-icons'>" \
                                                                                      "paid</span></button>" \
                                                                                      "<button name='view-order' " \
                                                                                      "value='"\
                                     + str(item.id) + "'type='submit'><span class='material-icons'>receipt</span>" \
                                                      "</button>"
                order_list_display.append(temp)
                order_list_display = sorted(order_list_display, key=lambda a: a['OrderID'], reverse=True)
            response = {
                "orders": order_list_display[0:5]
            }
            return JsonResponse(response)
    if request.method == 'POST':
        if 'pay-order' in request.POST:
            return payment(request)
        elif 'store_id_hidden' in request.POST:
            return account_details(request)
        elif 'view-order' in request.POST:
            # Order History
            order_id = request.POST.get('view-order')
            user = request.user
            store = context['store']
            order_details = models.Order.objects.get(id=order_id, user_id=user.id, store_id=store.id)
            view_order = rp.view_order(user_id=user.id, store_id=store.id, order_id=order_id)
            context['order'] = order_details
            context['order_item'] = view_order['table_django']
            order_hist_template = loader.get_template('Loyalty_X00152022/view-order.html')
            return HttpResponse(order_hist_template.render(context, request))
        elif 'submit' in request.POST:
            return scan(request)
        elif 'cancel' in request.POST:
            current_order = models.Order.objects.get(id=request.POST.get('cancel'))
            order_id = current_order.id
            if current_order.order_status == "PENDING":
                current_order.order_status = "CANCELLED"
                current_order.save()
            elif current_order.order_status == "NOT PLACED":
                current_order.delete()
            context['STATUS'] = "ORDER #" + str(order_id) + " CANCELLED"
            return HttpResponse(template.render(context, request))
        elif 'complete-payment' in request.POST:
            return payment(request)
        points = RewardPoints.objects.get(user_id=request.user.id,
                                          store_id=models.UserDetails.objects.get
                                          (user_id=request.user.id).store_selection_id)
        points_display = str(points.current_balance) + " Points"
        response = {"balance": points_display}
        return JsonResponse(response)
    return HttpResponse(template.render(context, request))


@login_required()
def choose_store(request):
    template = loader.get_template('Loyalty_X00152022/choose-store.html')
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    context['force_refresh'] = ""
    if request.method == "POST":
        if "choose-store-staff" in request.POST:
            new_store = request.POST.get('choose-store-staff')
            rp.change_store(user_id=request.user.id, store_id=new_store)
            if models.StoreUser.objects.get(user_id=request.user.id, store_id=new_store).user_type != "CUST":
                context['force_refresh'] = "<meta http-equiv='refresh' content='1; url = /shop/' />"
            else:
                context['force_refresh'] = "<meta http-equiv='refresh' content='1; /' />"
        elif "choose-store" in request.POST:
            new_store = request.POST.get('choose-store')
            rp.change_store(user_id=request.user.id, store_id=new_store)
            context['force_refresh'] = "<meta http-equiv='refresh' content='1; /' />"
    context['user'] = request.user
    staff = rp.staff_check(request)
    context['staff'] = staff
    select_options = ""
    # staff returns a list of store objects, or "Error..." or "NOT STAFF"; if neither of the latter, they're staff
    if staff != "Error - no Store is associated with this user" and staff != "NOT STAFF":
        store_list = models.StoreUser.objects.filter(user_id=request.user.id)
        temp_store_list = []
        store_list_full = models.Store.objects.all()
        for store in staff:
            select_options += "<option value='" + str(store.store_id)+"'>-STAFF--"\
                              + models.Store.objects.get(id=store.store_id).store_name + "</option>"
            temp_store = models.Store.objects.get(id=store.store_id)
            temp_store_list.append(temp_store)
        for store in store_list:
            if store not in staff:
                select_options += "<option value='" + str(store.store_id) + "'>"\
                                  + models.Store.objects.get(id=store.store_id).store_name + "</option>"
            temp_store = models.Store.objects.get(id=store.store_id)
            temp_store_list.append(temp_store)
        for store in store_list_full:
            if store not in temp_store_list:
                select_options += "<option value='" + str(store.id) + "'>-NEW--" \
                                  + models.Store.objects.get(id=store.id).store_name + "</option>"
    elif staff == "NOT STAFF":
        try:
            store_list = models.StoreUser.objects.get(user_id=request.user.id)
            store_list = models.StoreUser.objects.filter(user_id=request.user.id)
        except models.StoreUser.MultipleObjectsReturned:
            store_list = models.StoreUser.objects.filter(user_id=request.user.id)
        except models.StoreUser.DoesNotExist:
            # If no model exists, then return; else create list of all models of Store User to iterate over
            return HttpResponse(template.render(context, request))
        store_list_full = models.Store.objects.all()
        temp_store_list = []
        for store in store_list:
            select_options += "<option value='" + str(store.store_id) + "'>" \
                              + models.Store.objects.get(id=store.store_id).store_name + "</option>"
            temp_store = models.Store.objects.get(id=store.store_id)
            temp_store_list.append(temp_store)
        for store in store_list_full:
            if store not in temp_store_list:
                select_options += "<option value='" + str(store.id) + "'>-NEW--" \
                                  + models.Store.objects.get(id=store.id).store_name + "</option>"

    context['store_selection'] = select_options
    return HttpResponse(template.render(context, request))


@login_required()
def offers(request):
    template = loader.get_template('Loyalty_X00152022/offers.html')
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    context['user'] = request.user
    store = models.Store.objects.get(id=models.UserDetails.objects.get(user_id=request.user.id).store_selection_id)
    if context['user_type'] == "CUST":
        offers = models.Offers.objects.filter(store_id=store.id).order_by('date_end')
        today = datetime.date.today()
        offers_in_date = []
        for offer in offers:
            if offer.date_end >= today:
                offers_in_date.append(offer)
        context['offers'] = offers_in_date
    else:
        context['offers'] = models.Offers.objects.filter(store_id=store.id)
    context['store_user'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=store.id)
    staff = rp.staff_check(request=request)
    context['staff'] = staff
    if request.method == "POST":
        if request.POST.get('cart'):
            # If post contains cart, add to cart request
            offer_id = request.POST.get('cart')
            quantity = request.POST.get('qty')
            price = models.Offers.objects.get(id=offer_id).price
            user = request.user.id
            store = models.UserDetails.objects.get(user_id=user).store_selection_id
            order_addition = decimal.Decimal(decimal.Decimal(price) * decimal.Decimal(quantity))
            try:
                order = models.Order.objects.get(user_id=user, store_id=store, order_status="NOT PLACED")
            except models.Order.DoesNotExist:
                order = models.Order.objects.create(user_id=user, store_id=store, order_status="NOT PLACED")
            except models.Order.MultipleObjectsReturned:
                order = models.Order.objects.filter(user_id=user, store_id=store, order_status="NOT PLACED")[0]
            try:
                order_basket = models.OrderBasket.objects.get(order_id=order.id, offer_id=offer_id, user_id=user)
                order_basket.quantity += int(quantity)
            except models.OrderBasket.DoesNotExist:
                order_basket = models.OrderBasket.objects.create(order_id=order.id, user_id=user, store_id=store,
                                                                 quantity=quantity, offer_id=offer_id)
            order_basket.save()
            order.order_total += order_addition
            order.save()
            context['STATUS'] = "Success! Offer added to Cart<script>" \
                                "window.onload = function(){" \
                                "document.getElementById('view-order').click();" \
                                "document.getElementById('order-status').style.display = 'block';}</script>"
            return HttpResponse(loader.get_template('Loyalty_X00152022/scan.html').render(context, request))
        elif "request-checkout" in request.POST:
            return scan(request)
        elif "cancel-order" in request.POST:
            return scan(request)
        elif request.POST.get('save-offer'):
            print(request.POST)
            user = request.user.id
            store = models.UserDetails.objects.get(user_id=user).store_selection_id
            offer_id = int(request.POST.get('save-offer'))
            offer = models.Offers.objects.get(id=offer_id, store_id=store)
            new_price = decimal.Decimal(request.POST.get('offerpriceedit'))
            new_title = str(request.POST.get('offer-title'))
            new_text_short = str(request.POST.get('offer-text-short'))
            new_text_long = str(request.POST.get('offer-text-long'))
            new_end_date = request.POST.get('offer-end-date')
            new_start_date = request.POST.get('offer-start-date')
            offer.user_id = user
            offer.price = new_price
            offer.offer_title = new_title
            offer.offer_text_short = new_text_short
            offer.offer_text_long = new_text_long
            offer.date_end = new_end_date
            offer.date_start = new_start_date
            if request.POST.get('image-select') != "":
                if request.FILES['image-select']:
                    image = request.FILES['image-select']
                    fss = FileSystemStorage(location='Loyalty_X00152022/static/Offers')
                    fss.save(image.name, image)
                    offer.image_url = '/Offers/'+str(image)
            offer.save()
        elif request.POST.get('create-offer-save'):
            title = request.POST.get('create-offer-title')
            short_desc = request.POST.get('create-offer-text-short')
            long_desc = request.POST.get('create-offer-text-long')
            price = request.POST.get('create-offer-price')
            image = request.FILES['create-offer-image']
            date_start = request.POST.get('offer-start-date')
            date_end = request.POST.get('offer-end-date')
            fss = FileSystemStorage(location='Loyalty_X00152022/static/Offers')
            fss.save(image.name, image)
            models.Offers.objects.create(offer_title=title, offer_text_short=short_desc, offer_text_long=long_desc,
                                         image_url='/Offers/'+str(image), price=price, date_start=date_start,
                                         date_end=date_end, store_id=context['store'].id, user_id=request.user.id)

    return HttpResponse(template.render(context, request))


@login_required()
def shop(request):
    template = loader.get_template('Loyalty_X00152022/shop.html')
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    # Find if store user is member of staff at any store
    store = models.Store.objects.get(id=models.UserDetails.objects.get(user_id=request.user.id).store_selection_id)
    context['store_user'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=store.id)
    staff = rp.staff_check(request=request)
    print(request.POST)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get('id') == "pending-orders":
            all_pending_orders = models.Order.objects.filter(order_status="PLACED").order_by('-date')
            order_list_display = []
            for item in all_pending_orders:
                temp = {"OrderID": item.id, "CustName": item.user.first_name + " " + item.user.last_name,
                        "Amount": item.order_total, "Time": item.date.time(),
                        "Action": "<button id='approve"+str(item.id)+"'type='submit' method='post' "
                        "onclick=\'setIdHiddenOrder(this.id)\'>"
                        "<span class=\"material-icons\">"
                        "check_circle_outline</span></button>"
                        "<button id='manual" + str(item.id) + "'type='submit' method='post' "
                        "onclick=\'setIdHiddenOrder(this.id)\'>"
                        "<span class=\'material-icons\'>block</span></button>"}
                order_list_display.append(temp)
            response = {
                "orders": order_list_display
            }
            return JsonResponse(response)
        elif request.POST.get('id').__contains__('approve'):
            order_id = request.POST.get('id')[7:]
            update_order = models.Order.objects.get(id=int(order_id))
            update_order.order_status = "PENDING"
            update_order.save()
        elif request.POST.get('id').__contains__('manual'):
            order_id = request.POST.get('id')[6:]
            update_order = models.Order.objects.get(id=int(order_id))
            update_order.order_status = "MANUAL CHECKOUT"
            update_order.save()

    # Reward Points Functions
    context['points_form'] = forms.RewardPoints
    # Fetch & Display Balance

    # # Process Forms
    if request.method == "POST":
        if 'points-form-submit' in request.POST:
            update_balance_form = forms.RewardPoints(request.POST)
            if update_balance_form.is_valid():
                user_id = update_balance_form.cleaned_data.get("user_id")
                points_amount = update_balance_form.cleaned_data.get("points_amount")
                points_earned = update_balance_form.cleaned_data.get("points_earned")
                if points_earned == "Redeem Points":
                    if points_amount > 0:
                        points_amount = points_amount * -1
                check_balance = rp.check_balance(user_id=user_id, store_id=store.id)
                expected_balance = decimal.Decimal(check_balance) + decimal.Decimal(points_amount)
                status = rp.update_balance(user_id=user_id, store_id=store.id, new_points=points_amount)
                check_balance = rp.check_balance(user_id=user_id, store_id=store.id)
                if expected_balance == check_balance:
                    status = "Balance Successfully updated"
                    if points_earned == "Points from Sale":
                        new_total = models.RewardPoints.objects.get(user_id=user_id, store_id=store.id)
                        new_total.total_points_earned = decimal.Decimal(new_total.total_points_earned)\
                            + decimal.Decimal(points_amount)
                        new_total.save()
                    elif points_earned == "Give Points":
                        new_total = models.RewardPoints.objects.get(user_id=user_id, store_id=store.id)
                        new_total.total_points_given = decimal.Decimal(new_total.total_points_given) + \
                            decimal.Decimal(points_amount)
                        new_total.save()
                    elif points_earned == "Redeem Points":
                        new_total = models.RewardPoints.objects.get(user_id=user_id, store_id=store.id)
                        new_total.total_points_spent = decimal.Decimal(new_total.total_points_spent) +\
                            (decimal.Decimal(points_amount) * -1)
                        new_total.save()
                elif status == "Amount to redeem cannot exceed balance":
                    status = status
                else:
                    status = "Update Unsuccessful"

                context['status'] = status
        if 'new-rp-ratio' in request.POST:
            # Called by adjust_points (redirect & display message)
            context['msg'] = "<h3 id='order-status'>Reward Points Successfully Updated</h3>"

    context['staff'] = staff
    context["user"] = request.user
    context["forms"] = forms
    return HttpResponse(template.render(context, request))


@login_required()
def payment(request):
    template = loader.get_template('Loyalty_X00152022/payment.html')
    # Get user id of request (used to get store_id)
    request_user = request.user
    store_id = models.UserDetails.objects.get(id=request_user.id).store_selection_id
    get_order = None
    if "order-id" in request.POST or "order_id" in request.POST:
        try:
            get_order = models.Order.objects.get(id=request.POST.get('order-id')).order_total
        except models.Order.DoesNotExist:
            try:
                get_order = models.Order.objects.get(id=request.POST.get('order_id')).order_total
            except models.Order.DoesNotExist:
                return "No Order Found"
    elif "pay-order" in request.POST:
        try:
            get_order = models.Order.objects.get(id=request.POST.get('pay-order')).order_total
        except models.Order.DoesNotExist:
            return "No Order Found"
    rp_initial_val = models.Store.objects.get(id=store_id).rp_euro_ratio * get_order
    payment_form = forms.PaymentPreparationForm(initial={'total_points_earned': rp_initial_val})
    context = rp.get_store_selection(request)
    context['order_status'] = ""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get('id') == "rp-payment":
            # Triggered if user clicks "use reward points" - updates amount due
            context = {}
            order = models.Order.objects.get(id=request.POST.get('order_id'))
            user_rp_request = request.POST.get('rp_used')
            reward_points = rp.check_balance(store_id=order.store_id, user_id=order.user_id)
            if decimal.Decimal(user_rp_request) <= decimal.Decimal(reward_points):
                new_total = order.order_total
                new_total = decimal.Decimal(new_total) - decimal.Decimal(user_rp_request)
                new_points_earned = new_total * models.Store.objects.get(id=store_id).rp_euro_ratio
                context['points_spent'] = user_rp_request
                context['points_earned'] = new_points_earned
                context['balance'] = new_total
            else:
                context['balance'] = order.order_total
            return JsonResponse(context)
    elif request.method == "POST":
        if "complete-payment" in request.POST:
            # Validate form & carry out updates
            order_id = request.POST.get('order-id')
            points_spent = request.POST.get('total_points_spent')
            points_earned = decimal.Decimal(decimal.Decimal(request.POST.get('total_points_earned')))
            payment_method = request.POST.get('payment')
            if payment_method == "Paypal":
                # Payment not confirmed until signal set up
                # Stub account for now
                order = models.Order.objects.get(id=order_id)
                order.order_status = "AWAITING PAYMENT"
                order.save()
                context['order_status'] = "Awaiting Confirmation from Paypal!"
            elif payment_method == "InStore" or payment_method is None:
                # order complete - staff only hit "complete" once paid
                order = models.Order.objects.get(id=order_id)
                rp.check_balance(user_id=order.user_id, store_id=order.store_id)
                order.order_status = "COMPLETE"
                order.save()
                # Get reward points object for user attached to order
                rp_update = models.RewardPoints.objects.get(store_id=order.store_id, user_id=order.user_id)
                rp_update.total_points_spent += decimal.Decimal(points_spent)
                rp_update.total_points_earned += decimal.Decimal(points_earned)
                rp_update.save()
                rp_balance_adjustment = decimal.Decimal(decimal.Decimal(points_earned) - decimal.Decimal(points_spent))
                rp.update_balance(user_id=order.user_id, store_id=order.store_id, new_points=rp_balance_adjustment)
                context['order_status'] = "Order Complete - Thank You!"
            return HttpResponse(template.render(context, request))

    # Make sure order object exists
    try:
        # This "try" is for the Shop side
        try:
            order = models.Order.objects.get(id=request.POST.get('order_id'))
        # If that try fails, it is likely a Customer-side request
        except models.Order.DoesNotExist:
            order = models.Order.objects.get(id=request.POST.get('pay-order'))
        rp_balance = models.RewardPoints.objects.get(user_id=order.user_id, store_id=order.store_id).current_balance
        order_products = models.OrderBasket.objects.filter(order_id=order.id)
        product_list = []
        product_dict_temp = {}
        for item in order_products:
            if item.product_code is not None:
                product_dict_temp = {"Product": item.product_code.product_title,
                                     "QTY": item.quantity,
                                     "Amt": item.product_code.price,
                                     "SubTotal": decimal.Decimal(decimal.Decimal(item.quantity)
                                                                 * decimal.Decimal(item.product_code.price))}
            elif item.offer_id is not None:
                product_dict_temp = {"Product": models.Offers.objects.get(id=item.offer_id),
                                     "QTY": item.quantity,
                                     "Amt": models.Offers.objects.get(id=item.offer_id).price,
                                     "SubTotal": decimal.Decimal(decimal.Decimal(item.quantity)
                                                                 * decimal.Decimal(models.Offers.objects.get
                                                                                   (id=item.offer_id).price))}
            product_list.append(product_dict_temp)

        context['order'] = order.id
        context['user_id'] = order.user_id
        context["balance"] = rp_balance
        context["order_amt"] = order.order_total
        context["products"] = product_list
        context["form"] = payment_form
        return HttpResponse(template.render(context, request))

    except models.Order.DoesNotExist:
        order = "No order found."
        context['order'] = order
        return HttpResponse(template.render(context, request))


@login_required()
def checkout(request):
    template = loader.get_template('Loyalty_X00152022/checkout.html')
    store = models.Store.objects.get(id=models.UserDetails.objects.get(user_id=request.user.id).store_selection_id)
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    context['store_user'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=store.id)
    # Find if store user is member of staff at any store
    staff = rp.staff_check(request)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get('id') == "uid-checkout":
            try:
                user = models.User.objects.get(id=request.POST.get('user_id')).id
                store_id = models.UserDetails.objects.get(user_id=request.user.id).store_selection_id
                try:
                    order_id = models.Order.objects.get(user_id=user, store_id=store_id, order_status="NOT PLACED").id
                except models.Order.MultipleObjectsReturned:
                    order_id = models.Order.objects.filter(user_id=user, store_id=store_id,
                                                           order_status="NOT PLACED")[0].id
                except models.Order.DoesNotExist:
                    order = models.Order.objects.create(user_id=user, store_id=store_id, order_status="NOT PLACED")
                    order_id = order.id
            except models.User.DoesNotExist:
                user = "No User Found; please try again"
                order_id = "NO-ORDER"

            response = {
                "user_status": user,
                "order_id": order_id
            }
            return JsonResponse(response)
        if request.POST.get('id') == "add-to-order":
            order = models.Order.objects.get(id=request.POST.get('order_id'))
            product_code = models.Product.objects.get(product_code=str(request.POST.get('product_code')[14:])).id
            quantity = request.POST.get('quantity')
            try:
                order_basket = models.OrderBasket.objects.get(order_id=order.id, product_code_id=product_code)
                order_basket.quantity += int(quantity)
            except models.OrderBasket.DoesNotExist:
                order_basket = models.OrderBasket.objects.create(order_id=order.id, product_code_id=product_code,
                                                                 store_id=order.store_id, user_id=order.user_id,
                                                                 quantity=quantity)
            order_basket.save()
            order.order_total += (decimal.Decimal(models.Product.objects.get(id=product_code).price)
                                  * decimal.Decimal(quantity))
            order.save()
            response = {
                'cart': "Added to Order"
            }
            return JsonResponse(response)
        elif request.POST.get('id') == 'view-order-form':
            # Get all items on order
            user_id = request.user.id
            store_id = models.UserDetails.objects.get(user_id=user_id).store_selection_id
            order = models.Order.objects.get(id=request.POST.get('order_id'))
            table_data = rp.view_order(user_id=request.user.id, store_id=store_id, order_id=order.id)
            if type(table_data) != str:
                table_data = table_data['table_js']
            response = {
                'product': table_data,
                'total': order.order_total
            }
            return JsonResponse(response)
    # Reward Points Functions
    context['points_form'] = forms.RewardPoints
    # Fetch & Display Balance

    # # Process Forms
    if request.method == "POST":
        if 'points-form-submit' in request.POST:
            update_balance_form = forms.RewardPoints(request.POST)
            if update_balance_form.is_valid():
                user_id = update_balance_form.cleaned_data.get("user_id")
                store_id = staff[0].store_id
                points_amount = update_balance_form.cleaned_data.get("points_amount")
                points_earned = update_balance_form.cleaned_data.get("points_earned")
                if points_earned == "Redeem Points":
                    if points_amount > 0:
                        points_amount = points_amount * -1
                check_balance = rp.check_balance(user_id=user_id, store_id=store_id)
                expected_balance = decimal.Decimal(check_balance) + decimal.Decimal(points_amount)
                status = rp.update_balance(user_id=user_id, store_id=store_id, new_points=points_amount)
                check_balance = rp.check_balance(user_id=user_id, store_id=store_id)
                if expected_balance == check_balance:
                    status = "Balance Successfully updated"
                    if points_earned == "Points from Sale":
                        new_total = models.RewardPoints.objects.get(user_id=user_id,
                                                                    store_id=store_id)
                        new_total.total_points_earned = decimal.Decimal(new_total.total_points_earned) + \
                            decimal.Decimal(points_amount)
                        new_total.save()
                    elif points_earned == "Give Points":
                        new_total = models.RewardPoints.objects.get(user_id=user_id,
                                                                    store_id=store_id)
                        new_total.total_points_given = decimal.Decimal(new_total.total_points_given)\
                            + decimal.Decimal(points_amount)
                        new_total.save()
                    elif points_earned == "Redeem Points":
                        new_total = models.RewardPoints.objects.get(user_id=user_id,
                                                                    store_id=store_id)
                        new_total.total_points_spent = decimal.Decimal(new_total.total_points_spent)\
                            + (decimal.Decimal(points_amount) * -1)
                        new_total.save()
                elif status == "Amount to redeem cannot exceed balance":
                    status = status
                else:
                    status = "Update Unsuccessful"

                context['status'] = status
        elif 'cancel-order' in request.POST:
            models.Order.objects.get(id=request.POST.get('cancel-order')).delete()
        elif 'request-checkout' in request.POST:
            return payment(request)
        elif 'complete-payment' in request.POST:
            return payment(request)

    context['staff'] = staff
    context["user"] = request.user
    context["forms"] = forms
    return HttpResponse(template.render(context, request))


def register_view(request):
    # form_class = UserCreationForm
    # success_url = reverse_lazy('login')
    # template_name = 'registration/register.html'
    try:
        user_details_fetch = models.UserDetails.objects.get(user_id=request.user.id)
        staff_store = models.StoreUser.objects.get(user_id=request.user.id,
                                                   store_id=user_details_fetch.store_selection_id)
        staff_store = models.Store.objects.get(id=staff_store.id)
    except models.StoreUser.DoesNotExist:
        staff_store = None
    except models.UserDetails.DoesNotExist:
        staff_store = None
    form1 = forms.UserRegistrationForm()
    form2 = forms.UserRegistrationDetails()
    form3 = forms.ChooseStoreForm(initial={'store_name': staff_store})
    if request.user.is_authenticated:
        context = rp.get_store_selection(request)
        context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id,
                                                            store_id=context['store'].id).user_type
    elif not request.user.is_authenticated:
        context = {'login': "LOGIN"}
    # Single form - multiple models; chained dependency
    if request.method == "POST":
        form1 = forms.UserRegistrationForm(request.POST)
        form2 = forms.UserRegistrationDetails(request.POST)
        form3 = forms.ChooseStoreForm(request.POST)
        if all((form1.is_valid(), form2.is_valid(), form3.is_valid())):
            u = form1.save(commit=False)
            user = form1.save()
            form2 = form2.save(commit=False)
            form2.user_id = u.id
            store_selection = form3.save(commit=False)
            store_selection = models.Store.objects.get(store_name=store_selection)
            form2.save()
            user_details = models.UserDetails.objects.get(user_id=u.id)
            user_details.store_selection_id = store_selection.id
            user_details.save()
            login(request, user)
            # Set up other tables for user display
            models.StoreUser.objects.create(user_id=u.id, store_id=store_selection.id)
            models.RewardPoints.objects.create(user_id=u.id, store_id=store_selection.id)
            messages.success(request, "Registration Successful")
            try:
                check_req = models.StoreUser.objects.get(user_id=request.user.id,
                                                         store_id=models.UserDetails.objects.get
                                                         (user_id=request.user).store_selection_id)
                if check_req.user_type != "CUST":
                    return redirect("shop")
            except models.StoreUser.DoesNotExist:
                pass
            return redirect("index")
        else:
            messages.error(request, "Unsuccessful registration - invalid entry")
    context['UserRegistrationForm'] = form1
    context['UserRegistrationDetails'] = form2
    context['ChooseStoreForm'] = form3
    return render(request=request, template_name="registration/register.html",
                  context=context)


@login_required()
def contact(request):
    template = loader.get_template('Loyalty_X00152022/contact.html')
    context = rp.get_store_selection(request)
    addressurl = ""
    for i in context['store'].address:
        if i == " ":
            addressurl += "%20"
        else:
            addressurl += i
    context['addressurl'] = addressurl
    return HttpResponse(template.render(context, request))


@login_required()
def scan(request):
    template = loader.get_template('Loyalty_X00152022/scan.html')
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    # Points Balance
    # Use Filter once functionality for one store confirmed
    user = request.user
    store = models.Store.objects.get(id=models.UserDetails.objects.get(user_id=request.user.id).store_selection_id)
    try:
        selected_store = models.UserDetails.objects.get(user_id=request.user.id)
        points = RewardPoints.objects.get(user_id=request.user.id, store_id=selected_store.store_selection_id)
        context["balance"] = points
    except RewardPoints.DoesNotExist:
        points = models.RewardPoints.objects.create(user_id=user.id, store_id=store.id)
        points.save()

    # is_ajax() deprecated; replaced with XMLHttpRequest as per Django docs
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get('id') == "add-to-order":
            product_code = models.Product.objects.get(product_code=str(request.POST.get('product_code')[14:])).id
            unit_price = models.Product.objects.get(id=product_code).price
            user_id = request.user.id
            store_id = models.UserDetails.objects.get(user_id=user_id).store_selection.id
            quantity = request.POST.get('quantity')
            try:
                # If order exists, use this order
                orders_list = models.Order.objects.get(order_status="NOT PLACED", user_id=user_id)
                try:
                    order_basket = models.OrderBasket.objects.get(order_id=orders_list.id,
                                                                  product_code_id=product_code,
                                                                  store_id=store_id, user_id=user_id)
                    order_basket.quantity += int(quantity)
                except models.OrderBasket.DoesNotExist:
                    order_basket = models.OrderBasket.objects.create(order_id=orders_list.id,
                                                                     product_code_id=product_code,
                                                                     store_id=store_id, user_id=user_id,
                                                                     quantity=quantity)
                order_basket.save()
                orders_list.order_total += (decimal.Decimal(unit_price) * decimal.Decimal(quantity))
                orders_list.save()
            except models.Order.DoesNotExist:
                # if doesn't exist; create order
                order_total = decimal.Decimal(unit_price) * decimal.Decimal(quantity)
                new_order = models.Order.objects.create(user_id=user_id, store_id=store_id, order_status="NOT PLACED")
                new_order.save()
                try:
                    order_basket = models.OrderBasket.objects.get(order_id=new_order.id, product_code_id=product_code,
                                                                  store_id=store_id, user_id=user_id)
                    order_basket.quantity += int(quantity)
                except models.OrderBasket.DoesNotExist:
                    order_basket = models.OrderBasket.objects.create(order_id=new_order.id,
                                                                     product_code_id=product_code,
                                                                     store_id=store_id, user_id=user_id,
                                                                     quantity=quantity)
                order_basket.save()
                new_order.order_total = order_total
                new_order.save()

            response = {
                'cart': "Added to Cart"
            }
            return JsonResponse(response)
        elif request.POST.get('id') == 'view-order-form':
            # Get all items on order
            order_id = models.Order.objects.get(user_id=user.id, store_id=store.id, order_status="NOT PLACED")
            user_id = request.user.id
            store_id = models.UserDetails.objects.get(user_id=user_id).store_selection_id
            table_data = rp.view_order(user_id=request.user.id, store_id=store_id, order_id=order_id.id)
            if type(table_data) != str:
                table_data = table_data['table_js']
            response = {
                'product': table_data,
                'total': order_id.order_total
            }
            return JsonResponse(response)
        elif request.POST.get('id') == 'order-history':
            return index(request)
    elif request.method == "POST":
        if request.POST.get('cancel-order'):
            models.Order.objects.get(user_id=user.id, store_id=store.id, order_status="NOT PLACED").delete()
            context['STATUS'] = "Order Cancelled"
        elif request.POST.get('request-checkout'):
            update_status = models.Order.objects.get(user_id=user.id, store_id=store.id, order_status="NOT PLACED")
            update_status.order_status = "PLACED"
            update_status.save()
            context['STATUS'] = "Order Placed"
        elif 'pay-order' in request.POST:
            return payment(request)
        elif 'view-order' in request.POST:
            return index(request)
        elif 'complete-payment' in request.POST:
            return payment(request)
        elif 'submit' in request.POST:
            context['STATUS'] = "<script>window.onload = function() " \
                                "{document.getElementById('view-order').click();};</script>"
    context['store_id'] = store
    context["user"] = user
    context["balance"] = points
    context["forms"] = forms
    try:
        context["orders"] = models.Order.objects.get(user_id=user.id, store_id=store.id, order_status="NOT PLACED")
    except models.Order.DoesNotExist:
        context["orders"] = "NA"

    return HttpResponse(template.render(context, request))


# ajax_posting function
def ajax_posting(request):
    # is_ajax() deprecated; replaced with up to date protocol
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get('id') == "balance-check":
            user_id = request.POST.get('user_id', None)
            store_id = request.POST.get('store_id', None)
            if user_id and store_id:
                current_balance = rp.check_balance(store_id=store_id, user_id=user_id)
                if current_balance == "No User Found":
                    try:
                        models.User.objects.get(id=user_id)
                        display_balance = "<h1>User Not Registered with Store</h1>"
                    except models.User.DoesNotExist:
                        display_balance = "<h1>No User Found</h1>"
                else:
                    display_balance = "<h1>Current Balance: </h1><h1>" + str(current_balance) + "</h1>"
                response = {
                             'balance': display_balance
                }
                return JsonResponse(response)
        elif request.POST.get('id') == 'product-search':
            barcode = request.POST.get('ean_barcode')
            product_code = request.POST.get('product_code')
            store_id = models.UserDetails.objects.get(user_id=request.user.id).store_selection
            if product_code != "" or barcode != "":
                try:
                    search_result = models.Product.objects.get(store_id=store_id, product_code=product_code)
                    title = search_result.product_title
                    price = "€" + str(search_result.price)
                    manufacturer = "Manufacturer: " + search_result.manufacturer + \
                                   "<script>cartButtonsDisplay();</script>"
                    code = "Product Code: " + search_result.product_code
                except models.Product.DoesNotExist:
                    try:
                        search_result = models.Product.objects.get(store_id=store_id, ean_barcode=barcode)
                        title = search_result.product_title
                        price = "€" + str(search_result.price)
                        manufacturer = "Manufacturer: " + search_result.manufacturer + \
                                       "<script>cartButtonsDisplay();</script>"
                        code = "Product Code: " + search_result.product_code
                    except models.Product.DoesNotExist:
                        title = "No Product Found"
                        manufacturer = "Try Scan again, or enter the EAN/Product code below"
                        code = "Need Assistance? Ask a member of staff"
                        price = ""
            else:
                title = "No data received"
                code = "Or Enter Codes Manually below"
                price = ""
                manufacturer = "Scan Barcode via Camera"

            response = {
                'product_title': title,
                'product_code': code,
                'price': price,
                'manufacturer': manufacturer,
                'quantity': 1
            }
            return JsonResponse(response)
        elif request.POST.get('id') == 'update-order-total':
            new_quantity = request.POST.get('new_qty')
            try:
                int(new_quantity)
            except ValueError:
                new_quantity = 0
            item_code = request.POST.get('item_id')
            user_id = request.user.id
            store_id = models.UserDetails.objects.get(user_id=user_id).store_selection_id
            order_id = models.Order.objects.get(user_id=user_id, store_id=store_id, order_status="NOT PLACED")
            new_order_total = 0
            if item_code[0:3] == "OFR":
                offer_id = item_code[3:]
                order_basket = models.OrderBasket.objects.get(order_id=order_id.id, user_id=user_id,
                                                              store_id=store_id, offer_id=int(offer_id))
                order_adjustment = int(new_quantity) - int(order_basket.quantity)
                order_basket.quantity = new_quantity
                new_order_total += decimal.Decimal(order_adjustment) * models.Offers.objects.get(id=int(offer_id)).price
            else:
                product_id = item_code
                order_basket = models.OrderBasket.objects.get(order_id=order_id.id, user_id=user_id,
                                                              store_id=store_id, product_code_id=int(product_id))
                order_adjustment = int(new_quantity) - int(order_basket.quantity)
                order_basket.quantity = new_quantity

                new_order_total += decimal.Decimal(order_adjustment) * \
                    models.Product.objects.get(id=int(product_id)).price
            if int(new_quantity) == 0 or new_quantity == "":
                order_basket.delete()
            else:
                order_basket.save()
            order_id.order_total += new_order_total
            order_id.save()
            context = {'testy': "working"}
            return JsonResponse(context)


@login_required()
def account_details(request):
    template = loader.get_template('Loyalty_X00152022/account-details.html')
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    if request.method == "POST":
        store_user_acc = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id)
        store_user_form = forms.StoreUserAccountDetailsForm(request.POST, instance=store_user_acc)
        user_form = forms.UserAccountDetailsForm(request.POST, instance=request.user)
        user_details_form = forms.UserDetailsAccountDetailsForm(request.POST, instance=request.user.userdetails)
        if "submit-user-details" in request.POST:
            if all((user_form.is_valid(), user_details_form.is_valid(), store_user_form.is_valid())):
                user_form.save()
                update = user_details_form.save()
                update.save()
                current_selection = models.UserDetails.objects.get(user_id=request.user.id).store_selection_id
                rp.change_store(user_id=request.user.id, store_id=current_selection)
                check_storeuser_bool = models.StoreUser.objects.get(user_id=request.user.id, store_id=current_selection)
                if check_storeuser_bool.rp_acc_link is False:
                    store_user_acc.online_uid = store_user_form.cleaned_data.get('online_uid')
                    rp.link_account(rs_user_id=request.user.id, store_id=current_selection)
                context['msg'] = "Account Successfully Updated"
            else:
                context['msg'] = "** Form incomplete - fill out all fields"
    store_usr_instance = models.StoreUser.objects.get(store_id=context['store'].id, user_id=request.user.id)
    store_user_form = forms.StoreUserAccountDetailsForm(instance=store_usr_instance)
    user_form = forms.UserAccountDetailsForm(instance=request.user)
    user_details_form = forms.UserDetailsAccountDetailsForm(instance=request.user.userdetails)
    context['staff'] = rp.staff_check(request)
    context['user_form'] = user_form
    context['user_details_form'] = user_details_form
    context['store_user_form'] = store_user_form
    context['store_user'] = store_usr_instance

    return HttpResponse(template.render(context, request))


@login_required()
def adjust_points(request):
    staff = rp.staff_check(request)
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    template = loader.get_template('Loyalty_X00152022/adjust-points.html')
    user = request.user
    context['user'] = user
    store_user = models.StoreUser.objects.get(user_id=user.id, store_id=context['store'].id)
    context['store_user'] = store_user
    context['staff'] = staff
    if request.method == "POST":
        if "new-rp-ratio" in request.POST:
            new_ratio = request.POST.get('new-rp-ratio')
            context['store'].rp_euro_ratio = new_ratio
            context['store'].save()
            return shop(request)
    return HttpResponse(template.render(context, request))


@login_required()
def user_management(request):
    template = loader.get_template('Loyalty_X00152022/user-management.html')
    context = rp.get_store_selection(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    if request.method == "POST":
        if "user-mgmt-submit" in request.POST:
            store = models.Store.objects.get(id=models.UserDetails.objects.get
                                             (user_id=request.user.id).store_selection_id)
            user_to_change = models.User.objects.get(id=request.POST.get('user-mgmt-submit'))
            update_role = models.StoreUser.objects.get(user_id=user_to_change.id, store_id=store.id)
            update_role.user_type = request.POST.get('choose-role')
            update_role.save()
            context['status'] = "Role Successfully Updated"
    staff = rp.staff_check(request)
    context['staff'] = staff
    context['store_user'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id)
    store = context['store']
    store_users = models.StoreUser.objects.filter(store_id=store.id)
    user_list = []
    page = request.GET.get('page', 1)
    user_roles = models.StoreUser.user_choices
    for user in store_users:
        user_dict = {'ID': user.user_id,
                     'name': models.User.objects.get(id=user.user_id).first_name + " "
                     + models.User.objects.get(id=user.user_id).last_name,
                     }
        user_type_options = ""
        for role in user_roles:
            if role[1] != user.get_user_type_display() and role[1] != "ADMIN":
                user_type_options += "<option value='" + role[0] + "'>" + role[1] + "</option>"
            elif role[1] == "ADMIN":
                pass
            else:
                user_type_options += "<option value='" + user.user_type + "' selected>" + \
                                     user.get_user_type_display() + "</option>"
        user_dict['user_type'] = user_type_options

        user_list.append(user_dict)
    user_list_pagination = Paginator(user_list, 10)
    try:
        user_list_pagination = user_list_pagination.page(page)
    except PageNotAnInteger:
        user_list_pagination = user_list_pagination.page(1)
    except EmptyPage:
        user_list_pagination = user_list_pagination.page(user_list_pagination.num_pages)

    context['user_list'] = user_list_pagination
    return HttpResponse(template.render(context, request))


def support(request):
    template = loader.get_template('Loyalty_X00152022/support.html')
    context = rp.get_store_selection(request)
    return HttpResponse(template.render(context, request))


def submit_product(request):
    template = loader.get_template('Loyalty_X00152022/submit-product.html')
    context = rp.get_store_selection(request)
    context['staff'] = rp.staff_check(request)
    context['user_type'] = models.StoreUser.objects.get(user_id=request.user.id, store_id=context['store'].id).user_type
    if request.method == "POST" and request.FILES['product-csv']:
        # File upload
        product_update = request.FILES['product-csv']
        fss = FileSystemStorage(location='Loyalty_X00152022/static/product')
        fss.save(context['store'].store_name+"_" + str(request.user.id) + "_" + product_update.name, product_update)
        context['STATUS'] = "<h2>CSV Successfully uploaded - we will get to it ASAP!</h2>" \
                            "<meta http-equiv='refresh' content='6; /shop/' />"
    return HttpResponse(template.render(context, request))


@login_required()
def order_history(request):
    template = loader.get_template('Loyalty_X00152022/order-history.html')
    context = rp.get_store_selection(request)
    context['staff'] = rp.staff_check(request)
    img = qrcode.make(request.user.id, image_factory=qrcode.image.svg.SvgImage, box_size=20)
    stream = BytesIO()
    img.save(stream)
    context["svg"] = stream.getvalue().decode()
    if request.method == "POST":
        if "view-order" in request.POST:
            return index(request)
        elif "submit" in request.POST:
            return scan(request)
        elif "pay-order" in request.POST:
            return payment(request)
        elif "complete-payment" in request.POST:
            return payment(request)
        elif "cancel" in request.POST:
            return index(request)
    return HttpResponse(template.render(context, request))


@login_required()
def order_history_full(request):
    # Full Transaction History; paginated
    template = loader.get_template('Loyalty_X00152022/all-orders.html')
    context = rp.get_store_selection(request)
    context['staff'] = rp.staff_check(request)
    user = request.user
    if request.method == "POST":
        if "view-order" in request.POST:
            return index(request)
        elif "pay-order" in request.POST:
            return payment(request)
        elif "submit" in request.POST:
            return scan(request)
        elif "cancel" in request.POST:
            return index(request)
    try:
        # Check if any orders exist (if they do, override with filter
        orders = models.Order.objects.get(user_id=user.id, store_id=context['store'].id)
        orders = models.Order.objects.filter(user_id=user.id, store_id=context['store'].id).order_by('-id')
    except models.Order.DoesNotExist:
        return index(request)
    except models.Order.MultipleObjectsReturned:
        orders = models.Order.objects.filter(user_id=user.id, store_id=context['store'].id).order_by('-id')
    page = request.GET.get('page', 1)
    orders_list_pagination = Paginator(orders, 5)
    try:
        orders_list_pagination = orders_list_pagination.page(page)
    except PageNotAnInteger:
        orders_list_pagination = orders_list_pagination.page(1)
    except EmptyPage:
        orders_list_pagination = orders_list_pagination.page(orders_list_pagination.num_pages)
    context['orders'] = orders_list_pagination
    return HttpResponse(template.render(context, request))
