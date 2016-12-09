from . import basic_success, basic_failure, basic_error, db
from datetime import datetime

def item_list(opts, retailer_id, method):
	if method != "GET":
		return basic_failure("GET method only")
	store_id = opts['retailer_id']
	res=list();
	if store_id:
		try:
			data2= db.offers_alt.find({"retailer_id" :int(store_id)} , {"_id":False})
			for d in data2:
				data={};
				data['data']= db.items_alt.find_one({"item_id" :d['item_id']} , {"_id":False})
				data['data']['qrcodes']=list();
				temp=db.codes_alt.find({"offer_id":d['offer_id']  , "code":{'$exists':True}} , {"_id":False ,"code":True})
				for t in temp:
					(data['data']['qrcodes']).append(t['code'])
				res.append(data['data'])
			return basic_success(res)
		except:
			return basic_error("Invalid Store ID");
	else:
		return basic_error("Store id is not available");
	
	
def order_list(opts, retailer_id, method):
	if method != "POST":
		return basic_failure("POST method only")

    # Get the status required
	status = opts.get("status")
	type = opts.get("type")
	payment = opts.get("mode")
	# Data fetch from db
	if type:
		if type == "new":
			type_array = ["placed"]
		elif type == "past":
			type_array = ["delivered" , "cancelled"]
		elif type == "current":
			type_array = ["ready" , "accepted" , "delayed" , "processed"]
		else:
			return basic_error("Type Not defined")
		
		if type_array:
			data = list(db.orders.aggregate([
				{"$match": {
					"retailer_id": retailer_id,
					"status.0.status": {'$in':type_array} ,
					
				}},
				{"$sort": {"created_at": -1}},
				{"$project": {
					"_id": 0,
					"order_id": 1,
					"suborder_id": 1,
					"status": "$status.status",
					"address": 1,
					"created_at": 1,
					"order": 1,
					"payment_mode":1
					
				}}
			]))
	else:
		if status:
			data = list(db.orders.aggregate([
				{"$match": {
					"retailer_id": retailer_id,
					"status.0.status": status
					
				}},
				{"$sort": {"created_at": -1}},
				{"$project": {
					"_id": 0,
					"order_id": 1,
					"suborder_id": 1,
					"status": "$status.status",
					"address": 1,
					"created_at": 1,
					"order": 1,
					"payment_mode":1
				}}
			]))
		elif payment:
			data = list(db.orders.aggregate([
				{"$match": {
					"retailer_id": retailer_id, 
					"payment_mode":payment
					
				}},
				{"$sort": {"created_at": -1}},
				{"$project": {
					"_id": 0,
					"order_id": 1,
					"suborder_id": 1,
					"status": "$status.status",
					"address": 1,
					"created_at": 1,
					"order": 1,
					"payment_mode":1
				}}
			]))
		else:
			data = list(db.orders.aggregate([
				{"$match": {
					"retailer_id": retailer_id
					
				}},
				{"$sort": {"created_at": -1}},
				{"$project": {
					"_id": 0,
					"order_id": 1,
					"suborder_id": 1,
					"status": "$status.status",
					"address": 1,
					"created_at": 1,
					"order": 1,
					"payment_mode":1
				}}
			]))
    # Transform the data to get the price and stuff, todo: debatable
	for record in data:
		record['status'] = record['status'][0]
		order = record.pop('order')
		record['price'] = 0
		record['item_count'] = 0
		for item in order:
			record['price'] += int(item['price'])
			record['item_count'] += int(item['qty'])

	return basic_success(data)


def order_details(opts, retailer_id, method):
	try:
		if method != "POST":
			return basic_failure("POST method only")

		order_id = opts.get("order_id")
		suborder_id = opts.get("suborder_id")
		order = db.orders.find_one({"order_id":order_id , "retailer_id":retailer_id} , {"_id":0})
		if order:
			return basic_success(order)
		else:
			return basic_failure("Order Not Found")
	except:
		return basic_failure("Order Not Found")


def update_order(opts, retailer_id, method):
	try:
		if method != "POST":
			return basic_failure("POST method only")
		order_id = opts.get("order_id")
		suborder_id = opts.get("suborder_id")
		status = opts.get("status")
		push_query = {
			"status": {
				"$each": [{"status": status, "time": datetime.now()}],
				"$position": 0
			}
		}

		if status in ["cancelled","delayed","ready", "delivered","processed" ,"accepted"]:
			res=db.orders.update_one({"order_id": order_id,"suborder_id": suborder_id, "retailer_id": retailer_id}, {"$push": push_query})
			return basic_success((res.modified_count > 0))
		else:
			return basic_failure("Wrong Status")
	except:
		return basic_failure("Something went Wrong")	


def inner_scan(opts, retailer_id, method):
	try:
		code = opts.get("code")
		order_id = opts.get("order_id")
		offer_id = opts.get	("offer_id")	
		if not code or not order_id or not offer_id:
			return basic_error("Invalid parameters")
		code_data = db.qrcodes.find_one({"qrcodes": qc ,"retailer_id": retailer_id ,  "status": "live" , "used": False  }, {"_id": False })
		if not code_data:
			return basic_failure("Code not found")
		if code_data['used']:
			return basic_failure("Already used")
		qrcodes=db.orders.find_one({"order_id":order_id , "retailer_id": retailer_id} , {"_id":False , "order":True})
		for qrcode in qrcodes['order']:
			if code_data['item_id'] == qrcode['item_id']:
				return basic_success({
						"code": code,
						"item": qrcode,
						"codematch":True
				}) 
		return	basic_failure("This qrcode is not valid for this order")
	except Exception as e:
		return basic_error("Something Went wrong!")	

def new_scan(opts, retailer_id, method):
	code = opts.get("code")
	if not code:
		return basic_error("No code given")
	data = db.codes_alt.find_one({"code": code, "used": False}, {"code": True, "offer_id": True, "_id": False})
	if not data:
		return basic_failure("Already Used")
	else:
		offer = db.offers_alt.find_one({"offer_id":int(data['offer_id'])})
		item = db.items_alt.find_one({"item_id": offer['item_id']}, {"_id": False, "name": 1, "barcode": 1,"price":1, "img":1 , "weight":1})
		return basic_success({
			"code": code,
			"pts": offer['points'],
			"item": item
			
		})
