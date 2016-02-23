__author__ = 'Gopal'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse,basic_success,basic_failure,basic_error
import json
from datetime import datetime
failure = dumps({"success": 0})

@csrf_exempt
def list_item(request):
	try:
		data=db.items_alt
		result=data.find(projection={"_id":False})
		return basic_success(result)
	except:
		return basic_failure()
def list_vendor(request):
	try:
		data=db.vendors_alt
		result=data.find(projection={"_id":False , "vendor_id":1 , "name":1 , "address.address":1})
		return basic_success(result)
	except:
		return basic_failure()
def list_offers(request):
	try:
		data=db.codes_alt
		result=list(data.aggregate( [
			{
				"$match":{
					"used":False
				}
			},
			{ 
				'$group':{
					'_id':"$offer_id" ,
					"vendors":{
						'$addToSet':"$vendor_id"
					},
					"count": {"$sum": 1}
				}
			},
			{
				"$project": {
					"offer_id": "$_id",
					"_id": 0 , "count":1 , "vendors":1
				}
			}
		]))
		data=db.offers_alt
		aa = list(data.find({"expired":False},{"_id":False}))
		result1=list()
		for r in aa:
			for res in result: 
				if r['offer_id']==res['offer_id']:
					r['vendors']=res['vendors']
					result1.append(r)
		return basic_success(result1)
	except Exception as e:
		return basic_failure(e)
		