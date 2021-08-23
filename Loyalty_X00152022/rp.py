import decimal
from django.db import connections
from . import models


# Reward Squad External functions
# Keep the view a little more straightforward

# Check balance of online & in-store RP
def check_balance(user_id, store_id):
    # validate inputs
    try:
        user = models.User.objects.get(id=user_id)
    except models.User.DoesNotExist:
        user = None
        return "No User Found"
    try:
        store = models.Store.objects.get(id=store_id)
    except models.Store.DoesNotExist:
        store = None
        return "ERROR - Store ID expected, but not found"

    # Identify if user_id has online_uid
    online_uid = None
    try:
        online_uid = models.StoreUser.objects.get(store_id=store.id, user_id=user.id)
    except models.StoreUser.DoesNotExist:
        online_uid.online_uid = None
    # Get current balance (Reward Point Object)
    current_balance = models.RewardPoints.objects.get(store_id=store.id, user_id=user.id)
    if online_uid.online_uid is None or online_uid == "":
        pass
    else:
        # Code to fetch online RP balance
        # Only run if account has been linked
        if online_uid.rp_acc_link:
            online_rp = reward_point_balance(store_user=online_uid,
                                             store_rp=models.StoreOnlineRp.objects.get(store_id=store.id))
            if 0 < (current_balance.current_balance - online_rp) < 1 \
                    or 1 > (online_rp - current_balance.current_balance) > 0:
                # If the difference is between 0 & 1 either way, it's due to int vs decimal (between systems
                pass
            else:
                current_balance.current_balance = online_rp
                current_balance.save()
    current_balance = current_balance.current_balance
    return current_balance


def update_balance(user_id, store_id, new_points):
    # validate inputs
    try:
        user = models.User.objects.get(id=user_id)
    except models.User.DoesNotExist:
        user = None
        return "ERROR - User ID expected, but not found"
    try:
        store = models.Store.objects.get(id=store_id)
    except models.Store.DoesNotExist:
        store = None
        return "ERROR - Store ID expected, but not found"

    # Validate new_points before adding to balance
    try:
        new_points = decimal.Decimal(new_points)
    except ValueError:
        return "New Points not decimal.Decimal value"

    check_balance(user_id=user.id, store_id=store.id)
    current_balance = models.RewardPoints.objects.get(store_id=store.id, user_id=user.id)
    # Ensure balance will not be negative
    if new_points + current_balance.current_balance < 0:
        return "Amount to redeem cannot exceed balance"
    # Identify if user_id has online_uid
    try:
        online_uid = models.StoreUser.objects.get(store_id=store.id, user_id=user.id).online_uid
    except models.StoreUser.DoesNotExist:
        online_uid = None
    current_balance.current_balance = decimal.Decimal(round((decimal.Decimal(current_balance.current_balance) +
                                                             decimal.Decimal(new_points)), 2))
    if online_uid is None or online_uid == "":
        pass
    else:
        # Update Online Balance to match
        reward_point_balance(store_user=models.StoreUser.objects.get(user_id=user.id, store_id=store.id),
                             store_rp=models.StoreOnlineRp.objects.get(store_id=store.id),
                             action="Update", points_amount=new_points)

    current_balance.save()
    # Set the variable to the value, to return so new balance is known
    current_balance = current_balance.current_balance
    return current_balance


def staff_check(request):
    try:
        staff = models.StoreUser.objects.filter(user_id=request.user.id)
        temp_list = []
        for i in staff:
            if i.user_type != 'CUST':
                temp_list.append(i)
        if len(temp_list) == 0:
            # phrase used to identify if not a staff member; changes display on shop.html
            staff = "NOT STAFF"
        elif len(temp_list) > 0:
            staff = temp_list
        return staff

    except models.StoreUser.DoesNotExist:
        # Error should not be possible, but just in case
        return "Error - no Store is associated with this user"


def change_store(user_id, store_id, user_type="CUST"):
    try:
        user = models.User.objects.get(id=user_id)
    except models.User.DoesNotExist:
        return "Error - user not found"
    try:
        store = models.Store.objects.get(id=store_id)
    except models.Store.DoesNotExist:
        return "Error - store not found"
    try:
        store_user = models.StoreUser.objects.get(user_id=user.id, store_id=store.id)
    except models.StoreUser.DoesNotExist:
        store_user = models.StoreUser.objects.create(user_id=user.id, store_id=store.id, user_type=user_type)
    try:
        store_user_rp = models.RewardPoints.objects.get(user_id=user.id, store_id=store.id)
    except models.RewardPoints.DoesNotExist:
        store_user_rp = models.RewardPoints.objects.create(user_id=user.id, store_id=store.id)
    update_record = models.UserDetails.objects.get(user_id=user.id)
    update_record.store_selection_id = store.id
    update_record.save()
    return "Store Changed"


def view_order(user_id, order_id, store_id):
    order_items = models.OrderBasket.objects.filter(order_id=order_id, user_id=user_id, store_id=store_id)
    table_data_js = []
    table_data_django = []
    # Iterate over all items in basket, and put into a list for tabular view (one for JSON, one for Django Variable)
    temp_js = {}
    temp_django = {}
    for item in order_items:
        if item.product_code is not None:
            temp_js = {'CODE': item.product_code_id, 'QTY': "<input id='" + str(item.product_code_id) +
                                                     "'class='ordr-qty' type='number' min=0 value='" +
                                                    str(item.quantity)+"'>",
                       'PRODUCT': item.product_code.product_title, 'PRICE': item.product_code.price}
            temp_django = {'CODE': item.product_code_id,
                           'QTY': item.quantity,
                           'PRODUCT': item.product_code.product_title,
                           'PRICE': item.product_code.price}
        elif item.offer_id is not None:
            temp_js = {'CODE': "OFR"+str(item.offer_id), 'QTY': "<input id='"+"OFR"+str(item.offer_id) +
                                                         "'class='ordr-qty' type='number' min=0 value='" +
                                                         str(item.quantity)+"'>",
                       'PRODUCT': models.Offers.objects.get(id=item.offer_id).offer_title,
                       'PRICE': models.Offers.objects.get(id=item.offer_id).price}
            temp_django = {'CODE': str(item.offer_id),
                           'QTY': item.quantity,
                           'PRODUCT': models.Offers.objects.get(id=item.offer_id).offer_title,
                           'PRICE': models.Offers.objects.get(id=item.offer_id).price}
        table_data_js.append(temp_js)
        table_data_django.append(temp_django)
    table_data = {"table_js": table_data_js,
                  "table_django": table_data_django}
    return table_data


def get_store_selection(request):
    context = {
        'store': models.Store.objects.get(id=models.UserDetails.objects.get
                                          (user_id=request.user.id).store_selection_id),
        'icon_type': models.StoreUser.objects.get(user_id=request.user.id,
                                                  store_id=models.UserDetails.objects.get
                                                  (user_id=request.user.id).store_selection_id)}
    return context


def link_account(rs_user_id, store_id):
    # Get user model
    rsquad_user = models.User.objects.get(id=rs_user_id)
    # Get Store model
    store = models.Store.objects.get(id=store_id)
    # Get StoreUser model
    store_user = models.StoreUser.objects.get(user_id=rsquad_user.id, store_id=store.id)
    # if store is using online reward points, proceed
    if store_user.rp_acc_link is False:
        if store.online_rp:
            # Get StoreOnlineRp model
            try:
                store_rp = models.StoreOnlineRp.objects.get(store_id=store.id)
            except models.StoreOnlineRp.DoesNotExist:
                return "Store not set up with online reward points"
            if store_user.online_uid == "":
                return "Missing online user ID"
            else:
                ecom_type = models.StoreOnlineRp.objects.get(store_id=store.id).ecommerce_site_type
                if ecom_type.lower() == "OpenCart".lower():
                    # Build query & pass into execute
                    query = "SELECT * FROM %s WHERE %s=%s;" % (store_rp.user_table_name, store_rp.user_id_column_name,
                                                               store_user.online_uid)
                    store_db = connections[store_rp.database_name].cursor()
                    store_db.execute(query)
                    store_db.close()
                    link_account_bool = bool(False)
                    for i in store_db:
                        if (i[6] != rsquad_user.email) or (i[4] == rsquad_user.first_name and i[5] ==
                                                           rsquad_user.last_name) or (i[0] == store_user.online_uid):
                            link_account_bool = True
                    if link_account_bool:
                        store_user.rp_acc_link = True
                        store_user.save()
                        online_bal = reward_point_balance(store_user=store_user, store_rp=store_rp)
                        return store_user

        else:
            return "Store not set up with online reward points"
    else:
        return "Account is already linked"


def reward_point_balance(store_user, store_rp, action="Check", points_amount=0):
    ecom_type = store_rp.ecommerce_site_type
    # Expand offerings as required
    if store_rp.rp_column_name == "" or store_rp.rp_table_name == "":
        # Not setup with online reward points - custom RP required
        # Not currently offered; future developments can come up with earning system
        pass
    else:
        if ecom_type.lower() == "OpenCart".lower():
            if action.lower() == "Check".lower():
                # OpenCart reward points stored as transactions; balance is computed
                query = "SELECT %s FROM %s WHERE %s=%s;" % (store_rp.rp_column_name, store_rp.rp_table_name,
                                                            store_rp.user_id_column_name, store_user.online_uid)
                store_db = connections[store_rp.database_name].cursor()
                store_db.execute(query)
                store_db.close()
                rp_online_bal = 0
                for rp in store_db:
                    # Iterate over all records & get total
                    rp_online_bal += rp[0]
                return rp_online_bal
            elif action.lower() == "Update".lower():
                # update balance code
                points = int(round(points_amount))
                query = """
                insert into %s (customer_id, order_id, description, points, date_added)
                values (%s, 2, 'Reward Squad', %s, now());
                """ % (store_rp.rp_table_name, store_user.online_uid, points)
                store_db = connections[store_rp.database_name].cursor()
                store_db.execute(query)
                store_db.close()
        else:
            # Not presently setup, or developed for
            return "Not currently supported"
