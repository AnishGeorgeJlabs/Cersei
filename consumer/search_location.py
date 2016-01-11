__author__ = 'Pradeep'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import db

failure = dumps({"success": 0})

@csrf_exempt
def search_query(request):
    data = db.locations
    result = data.find(projection={"_id":False})
    success = dumps({"success": 1, "data": result, "totals": result.count()})
    return HttpResponse(success, content_type="application/json")


def get_location(request):
    data = db.locations
    try:
        area = request.GET['area']
    except:
        return HttpResponse(failure, content_type="application/json")
    query = {"area":area}
    result = data.find(query, {"_id":False,"locations": True})
    success = dumps({"success": 1, "data": result['data'][0]['location'], "total": result.count()})
    return HttpResponse(success, content_type="application/json")