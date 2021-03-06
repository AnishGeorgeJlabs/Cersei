from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import mock, security
from .vendor import order, account
from .retailer import retailer
from .consumer import show_offers, search_location,rewards, offers , scancode
from .fe import fe_offers , feapp_offers
from .fe_admin import feadmin
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
    # ------------ Onboarding URLs -------------------------
    url(r'^add_retailer$', security.m_auth(retailer.add_retailer)),
    url(r'^add_item$', security.m_auth(retailer.add_item)),
    url(r'^add_item_new$', security.m_auth(retailer.add_item_new)),
	url(r'^edit_retailer$', security.m_auth(retailer.edit_retailer)),
    url(r'^edit_item$', security.m_auth(retailer.edit_item)),
    url(r'^edit_item_new$', security.m_auth(retailer.edit_item_new)),
    url(r'^show_retailer$', security.m_auth(retailer.show_retailer)),
    url(r'^show_item$', security.m_auth(retailer.show_item)),
	url(r'^show_category$', security.m_auth(retailer.show_category)),
    url(r'^show_category_new$', security.m_auth(retailer.show_category1)),
    url(r'^show_company$', security.m_auth(retailer.show_company)),

	# ------------ Vendor URLs -------------------------
    url(r'^vendor/order/update', security.auth(order.update_order)),
    url(r'^vendor/order/scan$', security.auth(order.inner_scan)),
	url(r'^vendor/list_item$', security.auth(order.item_list)),
    url(r'^vendor/order/scan/new$', security.auth(order.new_scan)),
    url(r'^vendor/account', security.auth(account.vendor_account)),


    # ------------ Retailer URLs -------------------------
    url(r'^retailer/order/list$', security.rauth(order.order_list)),
    url(r'^retailer/order/details$',security.rauth(order.order_details)),
    url(r'^retailer/order/update', security.rauth(order.update_order)),
    url(r'^retailer/order/scan$', security.rauth(order.inner_scan)),
    url(r'^retailer/list_item$', security.rauth(order.item_list)),
    url(r'^retailer/order/scan/new$', security.auth(order.new_scan)),
    url(r'^retailer/account', security.rauth(order.retailer_account)),

    # ------------ Consumer URLs -----------------------
    #url(r'^consumer/location',  search_location.search_query),
    url(r'^consumer/show_offers',  show_offers.show_offers),
    url(r'^consumer/reward',rewards.activeRewards),
	url(r'^consumer/code' , scancode.scanCode),
	url(r'^consumer/offers',  offers.offers),
    url(r'^consumer/list_offers',  offers.list_offers),
    url(r'^consumer/show_referral',  security.uauth(offers.show_offers)),
    url(r'^consumer/order/list',  security.uauth(offers.orders_list)),
    url(r'^consumer/order',  security.uauth(offers.order)),
    url(r'^consumer/register',  offers.add_user),
    url(r'^consumer/phone',  offers.phone),
    url(r'^consumer/retailer',  offers.retailer),
    url(r'^consumer/location',  offers.list_location),
    url(r'^consumer/account',  security.uauth(offers.user_info)),
    
	#-------------FE APP URLs ---------------------------
	url(r'^fe/list_item', security.fe_auth(feapp_offers.list_item)),
	url(r'^fe/list_retailer', security.fe_auth(feapp_offers.list_retailer)),
	url(r'^fe/list_offer', security.fe_auth(feapp_offers.list_offers)),
    url(r'^fe/qrcodes', security.fe_auth(feapp_offers.list_qrcodes)),
	url(r'^fe/create_offers', security.fe_auth(feapp_offers.create_offers)),
    url(r'^fe/edit_offer', security.fe_auth(feapp_offers.edit_offer)),
	url(r'^fe/delete_offers', security.fe_auth(feapp_offers.delete_offers)),	
	
	#-------------FE Admin APP URLs ---------------------------
	url(r'^feadmin/create_user', security.fe_auth(feadmin.create_feuser)),
    url(r'^feadmin/list_fe', security.fe_auth(feadmin.list_fe)),
    url(r'^feadmin/remove', security.fe_auth(feadmin.remove_fe)),
    url(r'^feadmin/approve', security.fe_auth(feadmin.approve_offer)),
    url(r'^feadmin/send_msg', security.fe_auth(feadmin.send_message)),
    url(r'^feadmin/show_msg', security.fe_auth(feadmin.show_messages)),
		
	#-------------FE APP URLs ---------------------------
	url(r'^feapp/login', fe_offers.login),
	url(r'^feapp/logout', fe_offers.logout),
	url(r'^feapp/list_item', fe_offers.list_item),
	url(r'^feapp/list_vendor1', security.fe_auth(fe_offers.list_vendor1)),
	url(r'^feapp/list_vendor', fe_offers.list_vendor),
	url(r'^feapp/list_offer', fe_offers.list_offers),
	url(r'^feapp/create_offers', security.fe_auth(fe_offers.create_offers)),
    
    # ------------ Auth URLs ---------------------------
    url(r'^auth/login$', security.login),
    url(r'^auth/ulogin$', security.ulogin),
    url(r'^auth/rlogin$', security.rlogin),
    url(r'^auth/mlogin$', security.m_login),
    url(r'^auth/fe/login$', security.fe_login),
	url(r'^auth/change_pass$', security.change_password),
]


