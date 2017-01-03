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
		if status in  ["accepted" , "cancelled"]:
			res=db.orders.update_one({"order_id": order_id,"suborder_id": suborder_id, "retailer_id": retailer_id}, {"$push": push_query})
		elif status is "processed":
			qrcodes = opts.get("qrcodes")
			if not qrcodes:
				return basic_failure("please add qrcodes to order")
			current_order=db.orders.find_one({"order_id":order_id , "retailer_id": retailer_id} , {"_id":False  , "order":1})
			if len(qrcodes) is not int(current_order['total_quantity']):
				return basic_failure("No. of qrcodes must be equal to total quantity")
			for order_data in order:
				qrcode_data = {}
			code_data = db.qrcodes.find({"qrcodes": {'$in':qc} ,"retailer_id": retailer_id ,  "status": "live" , "used": False  }, {"_id": False })
				if not code_data:
					return basic_failure("Some of qrcodes are not valid");
				(qrcode_data[code_data['item_id']]).append()
			return basic_success((res.modified_count > 0))
		else:
			return basic_failure("Wrong Status")
	except:
		return basic_failure("Something went")	
