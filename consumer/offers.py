__author__ = 'Pradeep'
from bson.json_util import dumps
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
import sys , os
from . import db,jsonResponse,basic_success,basic_failure,basic_error , get_json
import json
import random
import string
from datetime import datetime

failure = dumps({"success":0})
@csrf_exempt
def list_location(request):
	try:
		results = db.retailer.aggregate([
			{
				'$project': {
					"_id":'$areas'
				}
			},
			{
				'$unwind': '$_id'
			},
			{
				'$group': {
					"_id" : '$_id.locality',
					"data":{
						'$addToSet':'$_id.sub-locality'
					}
				}
			}
		]);
		return basic_success(results);
		if results:
			location = dict()
			for result in results:
				for area in result['areas']:
					try:
						(location[(area['locality']).lower()]).add((area['sub-locality']).lower())
					except:
						location[(area['locality']).lower()]=set()
						(location[(area['locality']).lower()]).add((area['sub-locality']).lower())
			return basic_success(location)
		else:
			return basic_error("Details not found")
	except Exception as e:
		return basic_failure("Something went wrong!"+str(e))

@csrf_exempt
def order(data, user_id, method):
	try:
		if data:
			for key in ["user_id" , "name" , "address" , "email"  , "phone" , "order"]:
				if key not in data:
					return basic_error(key+" missing")
			search_term = datetime.today().strftime("%Y%m%d")
			collection = db.orders.find({"order_id":re.compile(search_term, re.IGNORECASE)}).sort("order_id" , -1)
			try:
				order_id = collection[0]['order_id'];
				order_id = order_id.replace(search_term,"")
			except:
				order_id = 0
			order_id = datetime.today().strftime("%Y%m%d") + (str(int(order_id) +1)).zfill(6)
			i=0
			data['order_id']= order_id
			order_data = list()
			total_cart = 0;
			total_cb = 0;
			data['cashback']= {}
			data['cashback']['total_cb']  = total_cb
			data['cashback']['type'] = list()
			for order in data['order']:
				total_cb1=0
				order_temp = {}
				order_temp['order_id'] =order_id
				order_temp['created_at']=(datetime.now() )
				order_temp['suborder_id'] = order_id	+ (str(i +1)).zfill(2)
				order['suborder_id'] = order_id	+ (str(i +1)).zfill(2)
				order_temp['user_id'] =data['user_id']
				order_temp['name'] = data['name']
				order_temp['email'] = data['email']
				order_temp['address'] = data['address'] 
				order_temp['phone'] = data['phone']
				order_temp['retailer_id'] = order['retailer_id']
				price = 0
				order_temp['status'] = list()
				order_temp_status={}
				order_temp_status['time'] = datetime.now()
				order_temp_status['status'] = "placed"
				(order_temp['status']).append(order_temp_status)
				order_temp['order_total']=0
				order['total'] = 0
				order_temp['total_quantity']=0
				order_temp['order']=list()
				for item in order['offers']:
					temp={}
					offer = db.offers.find_one({"offer_id":item['offer_id']} , {"_id":0 , "item_id":1 , "cashback":1 , } )
					if not offer:
						continue
					item_detail = db.inventory.find_one({"item_id":offer['item_id']})
					if not item_detail:
						continue
					temp['offer_id'] = item['offer_id']
					temp['item_id'] = item_detail['item_id']
					temp['cashback'] = offer['cashback']

					temp['name'] = item_detail['product_name']
					temp['pic'] = item_detail['img'][0]
					temp['barcode'] = item_detail['barcode']
					temp['price'] = int(item_detail['price'])
					temp['qty'] = item['qty']
					price = int(item['qty']) * int( item_detail	['price'])
					total_cb1 += int(price * (float(temp['cashback'])/100))
					temp['total']=price
					item['info'] = temp
					(order_temp['order']).append(temp)
					order_temp['order_total'] += price
					order['total'] += price
					order_temp['total_quantity'] += int(item['qty'])
					total_cart += price
				total_cb += total_cb1
				data['cashback']['total_cb'] = total_cb
				(data['cashback']['type']).append({"suborder_id":order_temp['suborder_id'] , "cashback":total_cb1})
				order_data.append(order_temp)
				i+=1
			for order in order_data:
				db.orders.insert(order)
			ref = db.referral_offers.find_one({"user_id":user_id , "used":False})
			if ref:
				if total_cart >= 200:
					cb = total_cart * .1
					if cb > 50:
						cb = 50
					data['cashback']['total_cb'] += cb
					(data['cashback']['type']).append({"suborder_id":"referral" , "cashback":cb})
					ref['used']=True
					ref['status']='processed'
					ref['order_id'] = order_id
					db.referral_offers.save(ref)
			return basic_success(data)

		else:
			return basic_error("Details not found")
	except Exception as e:
		return basic_failure(str(e)+"Something went wrong!")

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
	query = {"areas.locality": location, "areas.sub-locality":area }
	result = data.find(query ,{"_id":False , "retailer_id":True })
	data =db.offers
	retailers = list()
	for r in result:
		retailers.append(r['retailer_id'])
	query = {"retailer_id":{'$in':retailers} , "approved":True ,  "deleted_at" :{'$exists':False}}
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
	offers_data_orig =list()
	for r1 in offers_data:
		for code in codes:
			if code['offer_id']  == r1['offer_id']:
				r1['remaining_qrcodes']	 = code['count']
				offers_data_orig.append(r1)
	return basic_success(offers_data_orig);

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

@csrf_exempt
def order_list(data, user_id, method):
	try:
		data = db.orders.aggregate(
			[
				{
					'$match': {
						"user_id":user_id
					}
				},
				{

					'$sort' :{
						"created_at":1
					}	

				},
				{
					'$group': {
						"_id":'$order_id' ,
						"created_at":{'$max':'$created_at' }, 
						"order":{
							'$push':{
								"status":'$status.status',
								"suborder_id":'$suborder_id',
								"retailer_id":'$retailer_id',
								"order":'$order' , 
							}
						}
					}
				},
				{
					'$project': {
						"_id":1 ,
						"created_at": { '$dateToString': { 'format': "%Y-%m-%d %H:%M:%S", 'date': "$created_at" } }, 
						"order":1
					}
				}

			]
		);
		if data:
			return basic_success(data)
		else:
			return	basic_success([])
	except Exception as e:
		return basic_failure(str(e)+"User Not found")

@csrf_exempt
def orders_list(data, user_id, method):
	try:
		data = db.orders.aggregate(
			[
				{
					'$match': {
						"user_id":user_id
					}
				},
				{

					'$sort' :{
						"created_at":1
					}	

				},
				{
					'$project': {
						"_id":0 ,
						"created_at": { '$dateToString': { 'format': "%Y-%m-%d %H:%M:%S", 'date': "$created_at" } }, 
						"order":1 , 
						"name": 1 , 
						"email":1 , 
						"retailer_id":1 , 
						"address":1 , 
						"phone":1 , 
						"user_id":1 , 
						"total_quantity":1 , 
						"order_id":1 , 
						"suborder_id":1 , 
						"order_total":1 ,
						"status":1

					}
				}

			]
		);
		if data:
			return basic_success(data)
		else:
			return	basic_success([])
	except Exception as e:
		return basic_failure(str(e)+"User Not found")

@csrf_exempt
def add_user(request):
	# ------- Add new User ----------
	try:
		opts = get_json(request)
		for key in ['name' , 'mobile_no' , "email" ,'address', 'password']:
			if key not in opts:
				return basic_error(key+" missing")
		# Get User ID to add
		search_term = 'TC'+ datetime.today().strftime("%Y%m%d")
		mobile_no = opts['mobile_no']
		if not mobile_no.strip().isdigit() or len(mobile_no.strip()) != 10:
			return basic_success("Not a valid Number")
		collection = db.user.find_one({'$or':[ { "mobile_no":mobile_no.strip() } , {"email":opts['email']}]})
		if collection:
			return basic_failure("User Email ID or Mobile No. is already registered");
		try:
			collection = db.user.find(sort=[("user_id", -1)])
			r  = (collection[0]['user_id']).find(search_term)
			if r is 0:
				user_id = collection[0]['user_id'];
				user_id = user_id.replace(search_term,"")
			else:
				user_id='0';
		except:
			user_id = "0";
		referral_code_true = False
		if opts.get("referral_code"):
			data1 = db.user.find_one({"referral_code": opts["referral_code"]})
			if data1:
				referral_code_true = True
				referred_by = data1['user_id']
		referral_code = (opts['name'])[:3] + ''.join(random.choice(string.ascii_lowercase+string.digits) for i in range(5))
		user_id = search_term + (str(int(user_id) +1)).zfill(4)
		data = {}
		data['user_id']=user_id
		data['name']=opts['name']
		data['email']=opts['email']
		data['address']=opts['address']
		data['referral_code']=referral_code
		if referral_code_true:
			data['referred_by']=referred_by
		data['mobile_no']=mobile_no.strip()
		data['created_at']=(datetime.now())
		data['updated_at']=(datetime.now())
		db.user.insert(data);
		api_key =''.join(random.choice(string.ascii_uppercase +string.ascii_lowercase+'!@#$%^&*()' + string.digits) for _ in range(32))
		creds = {}
		creds['api_key']= api_key
		data['api_key']= api_key
		creds['last_login']= datetime.now()
		creds['username']= data['mobile_no']
		creds['password']= opts['password']
		creds['user_id']= user_id
		creds['type']= 'user'
		db.credentials.insert(creds)
		if referral_code_true:
			refer = {}
			refer['user_id'] = user_id
			refer['used'] = False
			refer['referred_by'] = referred_by
			refer['created_at'] = datetime.now()
			db.referral_offers.insert(refer)
		return basic_success(data)
	except Exception as e:
		return basic_error(str(e)+"Something went wrong!")


@csrf_exempt
def show_offers(data, user_id, method):
	try:
		live = db.referral_offers.find({"user_id":user_id , "used":False} , {"_id":0})
		old = db.referral_offers.find({"user_id":user_id , "used":True} , {"_id":0})
		return basic_success({"current_offers":live , "used_offers":old})
	except Exception as e:
		return basic_error(str(e)+"NO record found")


@csrf_exempt
def user_info(data, user_id, method):
	try:
		return basic_success(db.user.find_one({"user_id":user_id} , {"_id":0}))
	except Exception as e:
		return basic_error("NO record found")