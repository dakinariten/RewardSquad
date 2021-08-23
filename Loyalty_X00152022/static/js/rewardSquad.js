// Cookie (used for csrf token)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Navigation Functions

// Open Side Bar
function openNav() {
    document.getElementById("rSquadNav").style.width = "60%";
}

// Close Side Bar
function closeNav() {
  document.getElementById("rSquadNav").style.width = "0%";

    // Close Nav if clicked outside of menu
    document.addEventListener("click", function(event) {
	// Do nothing if click is inside menu
	if (event.target.closest(".sidenav") || event.target.closest("#navHamburger")) {
	  return;
    }
	// otherwise set width to 0 i.e. hide
	document.getElementById("rSquadNav").style.width = "0%";
});
}

// Display accordion body
function accordionBalance() {
let accList = document.getElementsByClassName("accordion");
for (let i = 0; i < accList.length; i++) {
    accList[i].addEventListener("click", function () { this.classList.toggle("active");
    let accordionBody = this.nextElementSibling;
    if (accordionBody.style.display === "block") {
      accordionBody.style.display = "none";
      accList[i].classList.remove("active");
    } else {
      accordionBody.style.display = "block";
    }
  });
}
}

// Set viewbox for QR Code
// Without this, scanner does not work
function qrCodeViewBox() {
    document.getElementsByTagName("svg")[0].setAttribute("viewBox","10 10 200 200");
}

// QR / Barcode Scanner Init
//Instanstiate one of the scanner instances
function qrScanBarcode() {
    // QR Scanner for Staff (scan UID of users)
    let lastResult, countResults = 0;
    document.getElementById('barcode-scanner-container').style.display = "block";
    document.getElementById('table').innerHTML = "";
    document.getElementById('product-search').style.display = "block";

    function onScanSuccess(decodedText) {
        if (decodedText !== lastResult) {
            ++countResults;
            lastResult = decodedText;
            // Handle on success condition with the decoded message.
            document.getElementById('id_ean_barcode').value = decodedText;
            // Once barcode has been decoded, set it to the input & click search
            document.getElementById('product-search-button').click();
            // Clear the scanner to keep screen space utilised
            html5QrcodeScanner.clear();
            // Disable close scan button
            document.getElementById('scan-a').style.visibility = "hidden";
            // Add Start Scanner Button
            document.getElementById('launch-cam-container').innerHTML += "<button style='margin-top: 2em' id='launch-cam' onclick='qrScanBarcode()'>Launch Camera</button>";
        }
    }
    let html5QrcodeScanner = new Html5QrcodeScanner(
        "qr-reader", {fps: 10, qrbox: 150});
    html5QrcodeScanner.render(onScanSuccess);
    // If "launch-cam" is not visible, make it so (vice versa)
    if (document.getElementById('launch-cam-container') != null) {
        document.getElementById('launch-cam-container').style.display = "none";
    }
    document.getElementById('scan-a').style.visibility = "visible";
    clearSelection();

}

// Close Scanner & Show Launch button
function closeScanner() {
    document.getElementById('barcode-scanner-container').style.display = 'none';
    document.getElementById('launch-cam-container').style.display = 'block';
    document.getElementById('launch-cam').style.display = 'block';
}

// Cart Buttons Hide/Display
function cartButtonsDisplay() {
    if (document.getElementById('product-price').innerHTML.includes('€')) {
    document.getElementById('order-buttons').style.display = 'block';
    $(document).ready(function(){
        $('order-buttons').children().css({'display': 'block'});});
    } else if (document.getElementById('product-price').innerHTML == "") {
        document.getElementById('order-buttons').style.display = 'none';
        $(document).ready(function(){
        $('order-buttons').children().css({'display': 'none'});});
    }
}

// Order Status - Display Settings
function orderStatusFade() {
    let status = document.getElementById('order-status').innerHTML;
    if (status == "") {
        document.getElementById('order-status').style.display = "none";
        $('#order-status').children().css({'display': 'none'});
    } else {
        setTimeout(function () {
            $('#order-status').fadeOut('fast');
        }, 5000);
    }
}

// Clear Product Selection
// return to normal state
function clearSelection() {
    document.getElementById('product-title').innerHTML = '';
    document.getElementById('product-code').innerHTML = '';
    document.getElementById('product-manufacturer').innerHTML = '';
    document.getElementById('product-price').innerHTML = '';
    cartButtonsDisplay();
}

// View Order
function viewOrder() {
    // Prepare the screen
    closeScanner();
    clearSelection();
    document.getElementById('product-search').style.display = "none";
    document.getElementById('launch-cam-container').style.display = "none";
    document.getElementById('continue-shopping').style.display = "block";
    document.getElementById('cancel-order').style.display = "block";
    document.getElementById('request-checkout').style.display = "block";

    // Ajax function using jQuery to process the data without need of a full DOM refresh
    $('#view-order-form').submit(function(e){
    e.preventDefault();
           $.ajax({
                type : "POST",
                url: $('#view-order-form').data('url'),
                data: {
                    id : "view-order-form",
                    order_id: $('#order-id-hidden').val(),
                 csrfmiddlewaretoken: csrftoken,
                 dataType: "json",
                },
                // Load data into table
                success: function(response){
                    let data = response.product;
                    let table = '<thead style="text-align: center;"><tr><th>CODE</th><th>QTY</th><th>Product</th><th>€</th></tr></thead><tbody>';
                    let totalText = "Total: €";
                    data.forEach(function(item){
                        // Set least important fields to hide by default on mobile; maximise screen real estate
                        table += '<tr><td class="mob-hide">'+item.CODE+'</td>';
                        table += '<td>'+item.QTY+'</td>';
                        table += '<td class="tbl-prod-title">'+item.PRODUCT+'</td>';
                        table += '<td>'+item.PRICE+'</td></tr>';
                    })
                    table += '<tr><td><script>evalOrderAmtProcPay();</script></td><td></td><td id="order-amt-tbl-summary" style="text-align: left; text-decoration-line: underline; text-decoration-style: double">'+totalText+response.total+'</td></tr>';
                    table += '</tbody>';
                    $('#table').empty().html(table);

                },
                failure: function() {
                }
            });
});
    document.getElementById('view-order').style.display = "none";
}

// Staff edit offers
// Contained in one Modal window; edit shows & hides all necessary inputs & buttons
function editOffers(offerID) {
    let offer_id = offerID;
    if (document.getElementById("offer-title-"+offer_id).style.display == "none") {
        document.getElementById("offer-title-" + offer_id).style.display = "block";
        document.getElementById("offertitle-" + offer_id).style.display = "none";
        document.getElementById("image-select-" + offer_id).style.display = "block";
        document.getElementById("offerimage-" + offer_id).style.display = "none";
        document.getElementById("offer-text-long-" + offer_id).style.display = "block";
        document.getElementById("offer-text-short-" + offer_id).style.display = "block";
        document.getElementById("offertextlong-" + offer_id).style.display = "none";
        document.getElementById("offerpriceedit-" + offer_id).style.display = "block";
        document.getElementById("offerpricedisplay-" + offer_id).style.display = "none";
        document.getElementById("save-offer-" + offer_id).style.display = "block";
        document.getElementById('qty-' + offer_id).style.display = "none";
        document.getElementById("cancel-" + offer_id).style.display = "block";
        document.getElementById('qtylabel-' + offer_id).style.display = "none";
        document.getElementById('edit-' + offerID).style.display = "none";
        document.getElementById('cart-' + offer_id).style.display = "none";
        document.getElementById('close-' + offerID).style.display = "none";
        document.getElementById("offer-start-date-"+ offer_id).style.display = "block";
        document.getElementById("offer-end-date-"+ offer_id).style.display = "block";
        let label_list = document.querySelectorAll('#offer-' + offerID + '-form label');
        for (let i = 0; i < label_list.length; i++) {
            if (label_list[i].id == "qtylabel-" + offer_id) {

            } else {
                label_list[i].style.display = "block";
            }
        }

    }

    $('#modal-'+offerID).on('hide.bs.modal', function () {
        document.getElementById("offer-title-" + offer_id).style.display = "none";
        document.getElementById("offertitle-" + offer_id).style.display = "block";
        document.getElementById("image-select-" + offer_id).style.display = "none";
        document.getElementById("offerimage-" + offer_id).style.display = "block";
        document.getElementById("offer-text-long-" + offer_id).style.display = "none";
        document.getElementById("offer-text-short-" + offer_id).style.display = "none";
        document.getElementById("offertextlong-" + offer_id).style.display = "block";
        document.getElementById("offerpriceedit-" + offer_id).style.display = "none";
        document.getElementById("offerpricedisplay-" + offer_id).style.display = "block";
        document.getElementById("save-offer-" + offer_id).style.display = "none";
        document.getElementById('qty-' + offer_id).style.display = "block";
        document.getElementById("cancel-" + offer_id).style.display = "none";
        document.getElementById('qtylabel-' + offer_id).style.display = "block";
        document.getElementById('edit-' + offerID).style.display = "block";
        document.getElementById('cart-' + offer_id).style.display = "block";
        document.getElementById('close-' + offerID).style.display = "block";
        document.getElementById("offer-start-date-"+ offer_id).style.display = "none";
        document.getElementById("offer-end-date-"+ offer_id).style.display = "none";
        let label_list = document.querySelectorAll('#offer-' + offerID + '-form label');
        for (let i = 0; i < label_list.length; i++) {
            if (label_list[i].id == "qtylabel-" + offer_id) {

            } else {
                label_list[i].style.display = "none";
            }
        }});
}

// Support Link change (depending on viewport)
function supportLinkDevice() {
    $(document).ready(function() {
        if (document.documentElement.clientWidth > 768) {
            document.getElementById('support-mail').setAttribute('href', '/support/');
    }
    });

}

// jQuery Update Order
function updateOrderQty() {

    $('#table-container').on('change', '.ordr-qty', function(){
        $.ajax({
                type : "POST",
                url: $('#table').data('url'),
                data: {
                    id : "update-order-total",
                 item_id : this.id,
                 new_qty: this.value,
                 csrfmiddlewaretoken: csrftoken,
                 dataType: "json",
                },
                success: function(){
                    document.getElementById('view-order').click();
                },
                failure: function() {
                }
            });
         $('#view-order-form').unbind('submit');
    });
}

// Reward Points - QR Scanner
function qrScanPoints() {
    let lastResult, countResults = 0;

    function onScanSuccess(decodedText) {
        if (decodedText !== lastResult) {
            ++countResults;
            lastResult = decodedText;
            // Handle on success condition with the decoded message
            if (!isNaN(decodedText)) {
                if (document.getElementById('error-output').style.display === "block") {
                    document.getElementById('error-output').innerHTML = "";
                }
                document.getElementById("id_user_id").value = decodedText;
                document.getElementById("user_id").value = decodedText;
                document.getElementById('error-output').style.display = "none";
                document.getElementById("balance-check-submit").click();
                document.getElementById('scan-header').style.display = "none";
                html5QrcodeScanner.clear();
            } else {
                document.getElementById('error-output').innerHTML = "<h1>Error - QR code not valid</h1>";
                document.getElementById('error-output').style.display = "block";
            }
        }
    }

    let html5QrcodeScanner = new Html5QrcodeScanner(
        "qr-reader", {fps: 10, qrbox: 150});
    html5QrcodeScanner.render(onScanSuccess);

}

// Show manual entry QR UID
function manualQrBalance() {
    document.getElementById('balance-check').style.display = "block";
    document.getElementById('user_id').type = 'number';
    document.getElementById('balance-check-submit').style.visibility = 'visible';
    document.getElementById('enter-manually').style.display = 'none';
}

// UID Scanner - Checkout
function qrUidCheckout() {
    let lastResult, countResults = 0;

    function onScanSuccess(decodedText) {
        if (decodedText !== lastResult) {
            ++countResults;
            lastResult = decodedText;
            // Handle on success condition with the decoded message.
            document.getElementById("uid-checkout-user").value = decodedText;
            document.getElementById("uid-checkout-submit").click();

            html5QrcodeScanner.clear();
        }
    }

    let html5QrcodeScanner = new Html5QrcodeScanner(
        "qr-reader1", {fps: 10, qrbox: 150});
    html5QrcodeScanner.render(onScanSuccess);

    // AJAX Call
    $('#uid-checkout').submit(function(e){
         e.preventDefault();
           $.ajax({
                type : "POST",
                url: $('#uid-checkout').data('url'),
                data: {
                    id : "uid-checkout",
                 user_id : $('#uid-checkout-user').val(),
                 csrfmiddlewaretoken: csrftoken,
                 dataType: "json",
                },
                success: function(data){
                    if(data.user_status !== "No User Found; please try again" ) {
                        //IF user is found, hide stage 1 and show stage 2
                        document.getElementById('checkout-stage-1').style.display = "none";
                        document.getElementById('checkout-stage-2').style.display = 'block';
                        document.getElementById('order-id-hidden').value = data.order_id;
                        //Hidden form field for request-checkout
                        document.getElementById('order_id').value = data.order_id;
                        document.getElementById('cancel-order').value = data.order_id;

                    } else {
                        document.getElementById('status').innerHTML = data.user_status;
                        setTimeout(function () {
                            $('#status').fadeOut('fast');
        }, 5000);
                    }
                },
                failure: function() {
                }
            });
                 // All code for processing AFTER submit

                 });

}
// Set value of hidden field (determine order ID and status to change)
// used by Pending Orders
function setIdHiddenOrder(order_id) {
    // set on dynamically generated elements; used in views.py
    document.getElementById('order-id-status').value = order_id;
}

// If order == €0; disable "proceed to payment"
function evalOrderAmtProcPay() {
    let orderAmount = document.getElementById('order-amt-tbl-summary').innerHTML;
    orderAmount = orderAmount.substring(8,);
    if (parseInt(orderAmount) === 0 ) {
        document.getElementById('request-checkout').disabled = true;
        document.getElementById('request-checkout').style.backgroundColor = "#4747470D";
    } else {
        document.getElementById('request-checkout').disabled = false;
        document.getElementById('request-checkout').style.backgroundColor = "#474747";
    }
}

// Toggle display for view order button (Scan)
function toggleViewOrderButton() {
    // Hide all unnecessary elements
    document.getElementById('view-order-container').style.display = "block";
    $(document).ready(function(){
        $('view-order-container').children().css({'display': 'block'});});
    document.getElementById('continue-shopping').style.display = "none";
    document.getElementById('cancel-order').style.display = "none";
    document.getElementById('request-checkout').style.display = "none";
    document.getElementById('view-order').style.display = "block";
}

// Determine if reward points link required
function shopRewardPoints() {
let place = window.location.href;
if (place.includes('#shop-rp-balance')) {
document.getElementById('balance').style.display = "block";
document.getElementById('shop-rp-balance').classList.add('active');}}

// Determine if order history should be shown (opened accordion on link)
function custOrderHistory() {
let place = window.location.href;
if (place.includes('#order-history-body')) {
    document.getElementById('order-history').click();
}
}


// Pay with Points
function payWithRP() {
    let rp_input = document.getElementById('reward-points-spent');
    if (rp_input.style.display === "") {
        rp_input.style.display = "block";
        rp_input.value = rp_input.getAttribute("max");
    } else {
        rp_input.style.display = "";
        rp_input.value = 0;
    }
    rpOrderTotalUpdate();
    rpManualEntry();

}

// Test for Logo display
function loadLogoIcon() {
    let logoimgurl = document.getElementById('foot-logo-img').getAttribute('src');
    let iconimgurl = document.getElementById('userIcon-img').getAttribute('src');
    document.getElementById('footLogo').style.backgroundImage = "url('" + logoimgurl + "')";
    document.getElementById('userIcon').style.backgroundImage = "url('" + iconimgurl + "')";
}

// AJAX Requests
function balanceCheckAjax() {
    $('#balance-check').submit(function(e){
         e.preventDefault();
           $.ajax({
                type : "POST",
                url: $('#balance-check').data('url'),
                data: {
                    id : "balance-check",
                 user_id : $('#user_id').val(),
                 store_id: $('#store_id').val(),
                 csrfmiddlewaretoken: csrftoken,
                 dataType: "json",
                },
                success: function(data){
                   $('#output').html(data.balance) /* response message */
                },
                failure: function() {
                }
            });
           document.getElementById('balance-check').style.display = "none";
           document.getElementById('scanContainer').style.display = "none";
           document.getElementById('launch-cam-qrbal').style.display = "block";
                 });
}

function customerBalanceCheck() {
    $('#balance-check').click(function () {
        $.ajax({
            type: "POST",
            url: $('#balance-check').data('url'),
            data: {
                csrfmiddlewaretoken: csrftoken
            },
            success: function (data) {
                let html = $(data).filter('#balance-check').html();
                $('#balance-output-h1').html(data.balance);
            }
        });
    });
}

// Order History - Customer View
function orderHistory() {
    $('#order-history').click(function (e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: $('#order-history-form').data('url'),
            data: {
                id: "order-history",
                csrfmiddlewaretoken: csrftoken
            },
            success: function(response){
                    let data = response.orders;
                    let table = '<thead style="text-align: center;"><tr><th>ID</th><th>€</th><th class="mob-hide">Date</th><th>Status</th><th>Action</th></tr></thead><tbody>';

                    data.forEach(function(item){
                        table += '<tr><td>'+item.OrderID+'</td>';
                        table += '<td>'+item.Amount+'</td>';
                        table += '<td class="mob-hide">'+item.Date+'</td>';
                        table += '<td>'+item.Status+'</td>';
                        table += '<td>'+item.Action+'<input id='+'"order-id-status"'+' type='+'"hidden"'+' value='+item.OrderID+'></td></tr>';
                    })
                    table += '<tr><input id='+'"order-id-status"'+' type='+'"hidden"'+' value='+'"item.OrderID"></tr>';
                    table += '</tbody>';
                    $('#order-table').empty().html(table);
                    let currentHTML = document.getElementById('table-container').innerHTML;
                    let full_page_link = "<button id='order-history-full' onclick='"+'location.href="/all-orders/"'+"' name='order-history-full' value='history' type='button'>View All Transactions</button>";
                    if (document.querySelectorAll('tbody > tr').length > 1) {
                    if (!document.getElementById('order-history-full')) { document.getElementById('table-container').innerHTML = currentHTML + full_page_link; }
                    }
                }
        });
    });
}

// Pending Orders (Shop View)
function pendingOrders() {
    $('#pending-orders').click(function () {
        $.ajax({
            type: "POST",
            url: $('#pending-orders').data('url'),
            data: {
                id: "pending-orders",
                csrfmiddlewaretoken: csrftoken
            },
            success: function(response){
                    let data = response.orders;
                    let table = '<thead style="text-align: center;"><tr><th>Name</th><th>€</th><th class="mob-hide">ID</th><th>Time</th><th>Approve</th></tr></thead><tbody>';

                    data.forEach(function(item){
                        table += '<tr><td>'+item.CustName+'</td>';
                        table += '<td>'+item.Amount+'</td>';
                        table += '<td class="mob-hide">'+item.OrderID+'</td>';
                        table += '<td>'+item.Time+'</td>';
                        table += '<td>'+item.Action+'</td></tr>';
                    })
                    table += '<tr><input id='+'"order-id-status"'+' type='+'"hidden"'+' value=""</tr>';
                    table += '</tbody>';
                    $('#order-table').empty().html(table);
                }
        });
    });
}

// Refresh Orders after approve/deny
function approveDenyPending() {

    $('#order-update').submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: $('#order-update').data('url'),
            data: {
                id: $('#order-id-status').val(),
                csrfmiddlewaretoken: csrftoken,
            }
        });
        // Double click pending-orders element to refresh element & auto update
        document.getElementById('pending-orders').click();
        document.getElementById('pending-orders').click();
    });

}

function productSearch() {
    $('#product-search').submit(function(e){
    e.preventDefault();
           $.ajax({
                type : "POST",
                url: $('#product-search').data('url'),
                data: {
                    id : "product-search",
                    ean_barcode : $('#id_ean_barcode').val(),
                    product_code : $('#id_product_code').val(),
                 csrfmiddlewaretoken: csrftoken,
                 dataType: "json",
                },
                success: function(data){
                    $('#product-title').html(data.product_title);
                    $('#product-code').html(data.product_code);
                    $('#product-code-hidden').val(data.product_code);
                    $('#product-price').html(data.price);
                    $('#product-price-hidden').val(data.price);
                    $('#quantity').val(data.quantity);
                    $('#product-manufacturer').html(data.manufacturer);
                },
                failure: function() {
                }
            });
    document.getElementById('id_product_code').value = "";
    document.getElementById('id_ean_barcode').value = "";
    document.getElementById('barcode-scanner-container').style.display = "none";
    document.getElementById('launch-cam-container').style.display = 'block';
    document.getElementById('launch-cam').style.display = 'block';
                 });
}

function addToOrder() {
    $('#add-to-order').submit(function(e){
    e.preventDefault();
           $.ajax({
                type : "POST",
                url: $('#add-to-order').data('url'),
                data: {
                    id : "add-to-order",
                    product_code : $('#product-code-hidden').val(),
                    quantity : $('#quantity').val(),
                    order_id: $('#order-id-hidden').val(),
                 csrfmiddlewaretoken: csrftoken,
                 dataType: "json",
                },
                success: function(data){
                    $('#order-status').html(data.cart)
                },
                failure: function() {
                }
            });
    if (document.getElementById('quantity').value !== "") {
        setTimeout(function() {document.getElementById('order-status').style.display = "block"; orderStatusFade();}, 200);

    }
    document.getElementById('quantity').value = "";
    document.getElementById('view-order-container').style.display = "block";
    $(document).ready(function(){
        $('view-order-container').children().css({'display': 'block'});});
    document.getElementById('continue-shopping').style.display = "none";
    document.getElementById('cancel-order').style.display = "none";
    document.getElementById('request-checkout').style.display = "none";
    setTimeout(function() {document.getElementById('view-order').click();}, 200);
});
}

// Update the balance of order (paying with RP)
function rpOrderTotalUpdate() {
    //Ajax call to update balance due
    $('#rp-payment').unbind('click');
    $('#rp-payment').click(function(e){
         e.preventDefault();
           $.ajax({
                type : "POST",
                url: $('#rp-payment').data('url'),
                data: {
                    id : "rp-payment",
                 rp_used : $('#reward-points-spent').val(),
                 order_id: $('#order-id-hidden').val(),
                 csrfmiddlewaretoken: csrftoken,
                 dataType: "json",
                },
                success: function(data){
                    if (data.balance == 0.0) {
                        document.getElementById('id_payment').style.display = "none";
                        document.getElementById('id_payment_0').required = false;
                        document.getElementById('id_payment_1').required = false;
                        $('#update-amount-due').html("Amount to Pay: €" + (data.balance));
                        $('#id_total_points_earned').val(data.points_earned);
                        $('#id_total_points_spent').val(data.points_spent);
                       } else {
                        document.getElementById('id_payment').style.display = "initial";
                        document.getElementById('id_payment_0').required = true;
                        document.getElementById('id_payment_1').required = true;
                        $('#update-amount-due').html("Amount to Pay: €" + (data.balance));
                        $('#id_total_points_earned').val(data.points_earned);
                        $('#id_total_points_spent').val(data.points_spent);
                    }
                },
                failure: function() {
                }
            });
                 });
}

// Number Input - Restrict manual entry
function rpManualEntry() {
    document.getElementById('reward-points-spent').oninput = function () {
        let max = parseFloat(this.max);
        if (this.value > max) {
            this.value = max;
        }
    }
    $('#reward-points-spent').on('change', function(){ document.getElementById('rp-payment').click();});
}

// Show-Hide QR Scan Balance (shop)
function relaunchLookup() {
    document.getElementById('scanContainer').style.display = "block";
    document.getElementById('enter-manually').style.display = "block";
    document.getElementById('user_id').value = "";
    document.getElementById('output').innerHTML = "";
    document.getElementById('launch-cam-qrbal').style.display = "none";
    qrScanBarcode();
}