from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import mock, security
from .vendor import order, account
from .consumer import show_offers, search_location,rewards

@csrf_exempt
def test(request):
    if request.method == "GET":
        extra = {
            "method": "GET",
            "requestData": request.GET
        }
    else:
        extra = {
            "method": "POST",
            "requestData": request.body
        }
    return JsonResponse({
        "result": True,
        "Message": "Test api, Welcome to project Cersei",
        "extra": extra
    })

urlpatterns = [
    url(r'^$', test),

    # ------------ Auth URL's ---------------------------
    url(r'^auth/login$', security.login),
    url(r'^auth/change_pass$', security.change_password),

    # ------------ Vendor URL's -------------------------
    url(r'^order/list$', security.auth(order.order_list)),
    url(r'^order/details$', mock.details),
    url(r'^order/update', security.auth(order.update_order)),
    url(r'^order/scan$', security.auth(order.inner_scan)),
    url(r'^order/scan/new$', security.auth(order.new_scan)),
    url(r'^retailer/account', security.auth(account.vendor_account)),

    # ------------ Consumer URL's -----------------------
    url(r'^location',  search_location.search_query),
    url(r'^show_offers',  show_offers.show_offers),
    url(r'^reward', rewards.activeRewards),

]


