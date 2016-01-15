__author__ = 'Pradeep'
from bson.json_util import dumps
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse,basic_success,basic_failure,basic_error
import json

failure = dumps({"success":0})

@csrf_exempt

def scanCode(request):
	try:
		code=request.GET['code']
		uID=request.GET['userid']
	except:
		return basic_error("Invalid Parameters")
	data=db.codes_alt
	result = data.find_one_and_update({"code":code , "status":{"$ne":"expired"}},{"$set":{"status":"available"} , "$addToSet":{"users":uID}})
	if result is None:
		return basic_failure();
	else:
		offerId= result['offer_id']
		data=db.index_offers
		result = data.find_one({'offers.offer_id':offerId} ,{"offers.$":True})
		if result is None:
			return basic_failure();
		result['offers'][0]['item']['points']=result['offers'][0]['points']
		return basic_success(result['offers'][0]['item'])
		
		