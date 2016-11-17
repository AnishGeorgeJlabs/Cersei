__author__ = 'Pradeep'
from bson.json_util import dumps
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
import sys , os
from . import db,jsonResponse,basic_success,basic_failure,basic_error , get_json
import json
from datetime import datetime

failure = dumps({"success":0})
@csrf_exempt
def order(request):
	try:
		data = get_json(request)
		if data:
			for key in ["user_id" , "name" , "address" , "email"  , "phone" , "order"]:
				if key not in data:
					return basic_error(key+" missing")
				search_term = datetime.today().strftime("%Y%m%d")
				collection = db.orders.find_one({"order_id":re.compile(search_term, re.IGNORECASE)})
				try:
					order_id = collection['order_id'];
					order_id = order_id.replace(search_term,"")
					
				except:
					order_id = 0
				order_id = datetime.today().strftime("%Y%m%d") + (str(int(order_id) +1)).zfill(6)
				i=0;
				order_data = list()
				for order in data['order']:
					order_temp = {}
					order_temp['order_id'] =order_id
					order_temp['created_at']=(datetime.now() )
					order_temp['suborder_id'] = order_id	+ (str(i +1)).zfill(2)
					order_temp['user_id'] =data['user_id']
					order_temp['name'] = data['name']
					order_temp['email'] = data['email']
					order_temp['address'] = data['address'] 
					order_temp['phone'] = data['phone']
					order_temp['retailer_id'] = order['retailer_id']
					price = 0
					order_temp['status'] = {}
					order_temp['status']['time'] = datetime.now()
					order_temp['status']['status'] = "placed"
					order_temp['order']=list()
					for item in order['items']:
						temp={}
						temp['name'] = item['name']
						temp['qty'] = item['qty']
						temp['barcode'] = item['barcode']
						temp['image'] = item['image']
						temp['price'] = item['price']
						(order_temp['order']).append(temp)
						price += int(temp['qty']) * int(temp['price'])
					order_temp['order_total'] = price
					order_data.append(order_temp)
					i+=1
			for order in order_data:
				db.orders.insert(order)
			return basic_success(order_data)

		else:
			return basic_error("Details not found")
	except Exception as e:
		return basic_failure("Something went wrong!"+str(e))






				

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
				offer['barcode']  = item['barcode']
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