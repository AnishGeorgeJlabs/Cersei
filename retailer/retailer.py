"""
	Api's for the onboarding App and all that stuff
"""
from django.views.decorators.csrf import csrf_exempt
from . import db, basic_success, basic_failure, basic_error
from datetime import datetime

@csrf_exempt
def retailer(request):
	collection = db.retailer.find_one(sort=[("retailer_id", -1)])
	try:
		retailer_id = collection['retailer_id'];
		retailer_id = retailer_id.replace("s","")
	except:
		retailer_id = "0";
	retailer_id = "s" + (str(int(retailer_id) +1)).zfill(4)
	return basic_success(retailer_id)



@csrf_exempt
def show_retailer(opts, manager_id, method):
	# ------- Show All Retailers ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		return basic_success(db.retailer.find({},{"_id":0}))
	except:
		return basic_error("Something went wrong!")

@csrf_exempt
def show_item(opts, manager_id, method):
	# ------- Show All Items ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		return basic_success(db.inventory.find({},{"_id":0}))
	except:
		return basic_error("Something went wrong!")

@csrf_exempt
def add_retailer(opts, manager_id, method):
	# ------- Add new Retailer ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		for key in ['name' , 'location' , "contact" ,'email','address' , 'areas']:
			if key not in opts:
				return basic_error(key+" missing")
		collection = db.retailer.find_one(sort=[("retailer_id", -1)])
		try:
			retailer_id = collection['retailer_id'];
			retailer_id = retailer_id.replace("s","")
		except:
			retailer_id = "0";
		retailer_id = "s" + (str(int(retailer_id) +1)).zfill(4)
		if (opts['location']).get('lat') and (opts['location']).get('lon'):
			data = {}
			data['retailer_id']=retailer_id
			data['name']=opts['name']
			data['location']=opts['location']
			data['contact']=opts['contact']
			data['email']=opts['email']
			data['address']=opts['address']
			data['areas']=opts['areas']
			data['add_by']=manager_id
			data['created_at']=(datetime.now())
			db.retailer.insert(data);
		return basic_success(retailer_id)
	except:
		basic_error("Something went wrong!")

@csrf_exempt
def add_item(opts, manager_id, method):
	# ------- Add new Item ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		for key in ['company_id' , 'product_name' , "barcode" ,'category','detail' , 'price' , 'weight' , 'mfg' , 'months']:
			if key not in opts:
				return basic_error(key+" missing")
		collection = db.inventory.find_one(sort=[("item_id", -1)])
		try:
			item_id = collection['item_id'];
			item_id = item_id.replace("IM","")
		except:
			item_id = "0";
		item_id = "IM" + (str(int(item_id) +1)).zfill(6)
		data = {}
		data['item_id']=item_id
		data['company_id']=opts['company_id']
		data['product_name']=opts['product_name']
		data['barcode']=opts['barcode']
		data['category']=opts['category']
		data['detail']=opts['detail']
		data['price']=opts['price']
		data['weight']=opts['weight']
		data['mfg']=opts['mfg']
		data['days']=opts['days']
		data['month']=opts['months']
		data['add_by']=manager_id
		data['created_at']=(datetime.now())
		db.inventory.insert(data);
		return basic_success(item_id)
	except:
		return basic_error("Something went wrong!")