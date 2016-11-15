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
	
	data=db.index_offers
	query = {"area":area , "location":location}
	result = data.find(query ,{"_id":False })
	return basic_success(result)
	
	
@csrf_exempt
def list_offers(request):
	try:
		location = request.GET['location']
		area=request.GET['area']
	except:
		return basic_error("Invalid Parameters")
	
	data=db.retailer
	query = {"areas.locality": location, "areas.sub-locality":area}
	result = data.find(query ,{"_id":False , "retailer_id":True })
	data =db.offers
	retailers = list()
	for r in result:
		retailers.append(r['retailer_id'])
	query = {"retailer_id":{'$in':retailers} , "approved":True}
	result1 = data.find(query  ,  {"_id":False})
	offers=list()
	items = list()
	offers_data = []
	
	for r1 in result1:
		offers.append(r1['offer_id'])
		items.append(r1['item_id'])
		offers_data.append(r1);
	# return basic_success(offers_data)
	data = db.inventory
	items = data.find({"item_id":{"$in":items}} , {"_id":False})
	for item in items:
		for offer  in offers_data:
			if item['item_id'] == offer['item_id']:
				offer['product_name'] = item['product_name']
				offer['detail'] = item['detail']
				offer['company_name'] = item['company_name']
				offer['weight']  = item['weight']
				offer['category_name'] = item['category_name']
				offer['img'] = item['img']
				offer['price'] = item['price']
	data=db.qrcodes	
	codes=list(data.aggregate( [
		{
			"$match":{
				"used":False , 
				"offer_id":{
					'$in':offers
				}
			}
		},
		{ 
			'$group':{
				'_id':"$offer_id" ,
				"count": {"$sum":1 }
			}
		},
		{
			"$project": {
				"offer_id": "$_id",
				"_id": 0 , "count":1 
			}
		}
	]))
	for r1 in offers_data:
		for code in codes:
			if code['offer_id']  == r1['offer_id']:
				r1['remaining_qrcodes']	 = code['count']
	return basic_success(offers_data);

@csrf_exempt
def retailer(request):
	try:
		location = request.GET['location']
		area=request.GET['area']
	except:
		return basic_error("Invalid Parameters")
	
	data=db.retailer
	query = {"areas.locality": location, "areas.sub-locality":area}
	result = data.find(query ,{"_id":False })
	return basic_success(result);