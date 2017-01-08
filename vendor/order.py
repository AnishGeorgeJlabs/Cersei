from . import basic_success, basic_failure, basic_error, db
from datetime import datetime

def item_list(opts, retailer_id, method):
	res=list();
	try:
		data2= db.offers.find({"retailer_id" :retailer_id} , {"_id":False})
		for d in data2:
			data={};
			data['data']= db.inventory.find_one({"item_id" :d['item_id']} , {"_id":False })
			temp=db.qrcodes.find({"offer_id":d['offer_id']  ,"used": False , "status":"live"} , {"_id":False ,"qrcodes":True})

			if temp:
				data['data']['stock'] = temp.count()
				qcode = list()
				for q in temp:
					qcode.append(q['qrcodes'])
				data['data']['qrcodes'] = qcode
				res.append(data['data'])
		return basic_success(res)
	except Exception as e:
		return basic_error(str(e)+"Invalid Store ID");
	
	
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
		if status in ["delayed","ready" ,"accepted" , "processed"]:
			res=db.orders.update_one({"order_id": order_id,"suborder_id": suborder_id, "retailer_id": retailer_id}, {"$push": push_query})
			return basic_success((res.modified_count > 0))
		if status is "processed1":
			res=db.orders.update_one({"order_id": order_id,"suborder_id": suborder_id, "retailer_id": retailer_id}, {"$push": push_query})
			qrcodes = opts.get("qrcodes")
			if not qrcodes:
				return basic_failure("please add qrcodes to order")
			current_order=db.orders.find_one({"order_id":order_id , "retailer_id": retailer_id} , {"_id":False  , "order":1})
			if len(qrcodes) is not int(current_order['total_quantity']):
				return basic_failure("No. of qrcodes must be equal to total quantity")
			code_data = db.qrcodes.find({"qrcodes": {'$in':qccodes} ,"retailer_id": retailer_id ,  "status": "live" , "used": False  }, {"_id": False })
			if len(qrcodes) is not code_data.count():
				return basic_failure("Some of qrcodes are not valid");
			update = {}
			update['used']=True
			update['used_at']=datetime.now()
			update['suborder_id']=suborder_id
			db.qrcodes.update({"qrcodes": {'$in':qccodes} ,"retailer_id": retailer_id ,  "status": "live" , "used": False  } , {'$set':update})
			return basic_success((res.modified_count > 0))
		if status in ["cancelled", "delivered"]:
			res=db.orders.update_one({"order_id": order_id,"suborder_id": suborder_id, "retailer_id": retailer_id}, {"$push": push_query})
			total = db.orders.find({"order_id":order_id}).count()
			total_processed = db.orders.find({"order_id":order_id , "status.0.status":{'$in':["cancelled", "delivered"]}}).count()
			if total  == total_processed:
				res2 = db.orders.aggregate([
					{
						'$match': {
							"order_id":order_id ,
							"status.0.status":"delivered"
						}
					},
					{
						'$unwind':'$order'
					},
					{
						'$group': {
							'_id':'order_id' , 
							'total':{'$sum':'$order_total'} , 
							"total_cashback":{'$sum':'$order.cashback'}
						}
					}
				]);
				if res2:
					total = 0
					is_referral =  db.referral_offers.find_one({"order_id":order_id , "status":'processed'})
					if is_referral:
						for re in res2: 
							if int(re['total']) >= 250:
								total = int(re['total'])/10
								if total > 50:
									total= 50
								db.referral_offers.update_one({"order_id":order_id} , {'$set':{'status':'used'}})
								if is_referral.get('referred_by'):
									db.referral_offers.insert({ "user_id":is_referral['referred_by'] , "used":False , "created_at":datetime.now()})
								push_query = {
									"cashback_history"+"."+datetime.now().strftime("%Y"): {
										"$each": [ {"cashback": total +int(re['total_cashback']), "order_id":order_id , "timestamp":  datetime.now().strftime("%d,%b") , "year":datetime.now().strftime("%Y") }],
										"$position": 0
									}
								}
					else:
						for re in res2:
							push_query = {
								"cashback_history"+"."+datetime.now().strftime("%Y"): {
										"$each": [ {"cashback": int(re['total_cashback']), "order_id":order_id , "timestamp":  datetime.now().strftime("%d,%b") , "year":datetime.now().strftime("%Y") }],
										"$position": 0
									}
								}
					res1 = db.orders.find_one({'suborder_id':suborder_id})
					db.user.find_one_and_update({"user_id":res1['user_id']} , {'$push':push_query , '$inc':{'total_cashback':total + int(re['total_cashback']) , 'account_balance':total + int(re['total_cashback'])} })
			return basic_success((res.modified_count > 0))
		return basic_failure("Wrong Status")
	except Exception as e:
		return basic_failure(str(e)+"Something went Wrong")	


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


def retailer_account(opts, retailer_id, method):
    # ------- retailer details ----------
    retailer = db.retailer.find_one({"retailer_id": retailer_id}, {"_id": False, "retailer_id": False})
    if not retailer:
        return basic_failure("Invalid retailer")

    # ------- account stats -----------
    retailer1= {}
    retailer1.update({
        "pending": 0,
        "cancelled": 0,
        "complete": 0,
        "total_points": 0
    })
    for item in db.orders.find({"retailer_id": retailer_id}, {"_id": False, "status": True}):
        status = item['status'][0]['status']

        if status == "placed":
            retailer1['pending'] += 1
        elif status == "accepted":
            retailer1['complete'] += 1
        else:
            retailer1['cancelled'] += 1

        retailer1['total_points'] =100

    return basic_success(retailer1)