from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import mock, security
from .vendor import order, account
from .retailer import retailer
from .consumer import show_offers, search_location,rewards, offers , scancode
from .fe import fe_offers
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
    # ------------ Onboarding URL's -------------------------
    url(r'^add_retailer$', security.m_auth(retailer.add_retailer)),
    url(r'^add_item$', security.m_auth(retailer.add_item)),
	url(r'^edit_retailer$', security.m_auth(retailer.edit_retailer)),
    url(r'^edit_item$', security.m_auth(retailer.edit_item)),
    url(r'^show_retailer$', security.m_auth(retailer.show_retailer)),
    url(r'^show_item$', security.m_auth(retailer.show_item)),

	# ------------ Vendor URL's -------------------------
    url(r'^vendor/order/list$', security.auth(order.order_list)),
    url(r'^vendor/order/details$', mock.details),
    url(r'^vendor/order/update', security.auth(order.update_order)),
    url(r'^vendor/order/scan$', security.auth(order.inner_scan)),
	url(r'^vendor/list_item$', security.auth(order.item_list)),
    url(r'^vendor/order/scan/new$', security.auth(order.new_scan)),
    url(r'^vendor/account', security.auth(account.vendor_account)),

    # ------------ Consumer URL's -----------------------
    url(r'^consumer/location',  search_location.search_query),
    url(r'^consumer/show_offers',  show_offers.show_offers),
    url(r'^consumer/reward',rewards.activeRewards),
	url(r'^consumer/code' , scancode.scanCode),
	url(r'^consumer/offers',  offers.offers),
    
	#-------------FE APP URL's ---------------------------
	url(r'^feapp/login', fe_offers.login),
	url(r'^feapp/logout', fe_offers.logout),
	url(r'^feapp/list_item', fe_offers.list_item),
	url(r'^feapp/list_vendor1', security.fe_auth(fe_offers.list_vendor1)),
	url(r'^feapp/list_vendor', fe_offers.list_vendor),
	url(r'^feapp/list_offer', fe_offers.list_offers),
	url(r'^feapp/create_offers', security.fe_auth(fe_offers.create_offers)),
    
    # ------------ Auth URL's ---------------------------
    url(r'^auth/login$', security.login),
    url(r'^auth/mlogin$', security.m_login),
    url(r'^auth/fe/login$', security.fe_login),
	url(r'^auth/change_pass$', security.change_password),
]


