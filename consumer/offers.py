__author__ = 'Pradeep'
from bson.json_util import dumps
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse,basic_success,basic_failure,basic_error
import json
from datetime import datetime

failure = dumps({"success":0})

@csrf_exempt
def offers(request):
	try:
		location = request.GET['location']
		area=request.GET['area']
	except:
		return basic_error("Invalid Parameters")
	cur_time= datetime.now()
	data=db.index_dummy
	query = {"area":area , "location":location , "offers.expiry":{"$gte":cur_time}  }
	result = data.find(query ,{"_id":False })
	return basic_success(result)
	
	