from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import mock, security, order

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
    url(r'^orders$', security.auth(order.order_list)),
    url(r'^orders/details$', mock.details),
    url(r'^orders/update', security.auth(order.update_order)),
    url(r'^scan$', mock.scan),


    url(r'^auth/login$', security.login),
    url(r'^auth/change_pass$', security.change_password)
]


