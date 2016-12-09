"""
	Api's for the onboarding App and all that stuff
"""
from django.views.decorators.csrf import csrf_exempt
from . import db, basic_success, basic_failure, basic_error
from datetime import datetime

@csrf_exempt
def show_category(opts, manager_id, method):
	# ------- Show All Retailers ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		return basic_success(db.categories.find({},{"_id":0 , "category_name":1 , "category_id":1}))
	except:
		return basic_error("Something went wrong!")

@csrf_exempt
def show_company(opts, manager_id, method):
	# ------- Show All Retailers ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		return basic_success(db.companies.find({},{"_id":0 , "company_name":1 , "company_id":1}))
	except:
		return basic_error("Something went wrong!")

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
def edit_retailer(opts, manager_id, method):
	# ------- Add new Retailer ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		if 'retailer_id' not in opts:
			return basic_error("Retailer ID missing")
		for key in ['name' , 'location' , "contact" ,'email','address' , 'areas','min_order']:
			if key not in opts:
				return basic_error(key+" missing")
		if (opts['location']).get('lat') and (opts['location']).get('lon'):
			data = {}
			h= db.retailer.find_one({"retailer_id":opts['retailer_id']})
			result = db.retailer.delete_one({"retailer_id":opts['retailer_id']})
			if result.deleted_count:
				data['retailer_id']=opts['retailer_id']
				data['name']=opts['name']
				data['location']=opts['location']
				data['contact']=opts['contact']
				data['email']=opts['email']
				data['address']=opts['address']
				data['areas']=opts['areas']
				data['min_order']=opts['min_order']
				data['add_by']=h['add_by']
				data['updated_by']=manager_id
				data['created_at']=h['created_at']
				data['updated_at']=(datetime.now())
				db.retailer.insert(data);
				return basic_success(opts['retailer_id'])
			else:
				return basic_error("Something went wrong!")
	except:
		return basic_error("Something went wrong!")

@csrf_exempt
def edit_item(opts, manager_id, method):
	# ------- Add new Item ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		if 'item_id' not in opts:
			return basic_error("Item ID missing")
		for key in [ 'product_name' , "barcode" ,'detail' , 'price' , 'weight'  , 'shelf_life']:
			if key not in opts:
				return basic_error(key+" missing")
		if "category_id" not in opts and "category_name" not in opts:
			return basic_error("Category details missing")
		if "company_id" not in opts and "company_name" not in opts:
			return basic_error("Company details missing")
			
			
		
		#Add Category 
		
		if "category_id" not in opts:
			category_name = opts.get("category_name")
			collection = db.categories.find_one(sort=[("category_id", -1)])
			try:
				cat_id = collection['category_id'];
				cat_id = cat_id.replace("CAT","")
			except:
				cat_id = "0";
			cat={}
			category_id = "CAT" + (str(int(cat_id) +1)).zfill(4)
			cat['category_id'] = "CAT" + (str(int(cat_id) +1)).zfill(4)
			cat['category_name'] = category_name
			cat['created_at']=(datetime.now())
			cat['add_by']=manager_id
			db.categories.insert(cat)
		else:
			category_id = opts['category_id']
			
			
		#add Company
		
		if "company_id" not in opts:
			company_name = opts.get("company_name")
			collection = db.companies.find_one(sort=[("company_id", -1)])
			try:
				com_id = collection['company_id'];
				com_id = com_id.replace("COM","")
			except:
				com_id = "0";
			com={}
			company_id="COM" + (str(int(com_id) +1)).zfill(4)
			com['company_id'] = "COM" + (str(int(com_id) +1)).zfill(4)
			com['company_name'] = company_name
			com['created_at']=(datetime.now())
			com['add_by']=manager_id
			db.companies.insert(com)
		else:
			company_id=opts['company_id']
			
		
		#add Item 
		h= db.inventory.find_one({"item_id":opts['item_id']})
		result = db.inventory.delete_one({"item_id":opts['item_id']})
		if result.deleted_count:
			data = {}
			data['item_id']=opts['item_id']
			data['company_id']=company_id
			data['company_name']=opts['company_name']
			data['category_id']=category_id
			data['category_name']=opts['category_name']
			data['product_name']=opts['product_name']
			data['barcode']=opts['barcode']
			data['detail']=opts['detail']
			data['price']=opts['price']
			data['weight']=opts['weight']
			data['shelf_life']=opts['shelf_life']
			data['updated_by']=manager_id
			data['updated_at']=(datetime.now())
			data['add_by']= h['add_by']
			if 'img' in opts:
				data['img'] = opts['img']
			else:
				data['img']=["http://jlabs.co/no_image.png"]
			data['created_at']=h['created_at']
			db.inventory.insert(data);
			return basic_success(opts['item_id'])
		else:
			return basic_error("Something went wrong!")
		
	except:
		return basic_error("Something went wrong!")
		
@csrf_exempt
def add_retailer(opts, manager_id, method):
	# ------- Add new Retailer ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		for key in ['name' , 'location' , "contact" ,'email','address' , 'areas' , "min_order"]:
			if key not in opts:
				return basic_error(key+" missing")
		# Get Retailer ID to add
		collection = db.retailer.find_one(sort=[("retailer_id", -1)])
		try:
			retailer_id = collection['retailer_id'];
			retailer_id = retailer_id.replace("RET","")
		except:
			retailer_id = "0";
		retailer_id = "RET" + (str(int(retailer_id) +1)).zfill(5)
		if (opts['location']).get('lat') and (opts['location']).get('lon'):
			data = {}
			data['retailer_id']=retailer_id
			data['name']=opts['name']
			data['location']=opts['location']
			data['contact']=opts['contact']
			data['email']=opts['email']
			data['address']=opts['address']
			data['areas']=opts['areas']
			data['min_order']=opts['min_order']
			data['add_by']=manager_id
			data['created_at']=(datetime.now())
			data['updated_at']=(datetime.now())
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
		for key in [ 'product_name' , "barcode" ,'detail' , 'price' , 'weight'  , 'shelf_life']:
			if key not in opts:
				return basic_error(key+" missing")
		if "category_id" not in opts and "category_name" not in opts:
			return basic_error("Category details missing")
		if "company_id" not in opts and "company_name" not in opts:
			return basic_error("Company details missing")
			
			
		# GET Item ID 
		collection = db.inventory.find_one(sort=[("item_id", -1)])
		try:
			item_id = collection['item_id'];
			item_id = item_id.replace("IM","")
		except:
			item_id = "0";
		item_id = "IM" + (str(int(item_id) +1)).zfill(7)
		
		
		#Add Category 
		
		if "category_id" not in opts:
			category_name = opts.get("category_name")
			collection = db.categories.find_one(sort=[("category_id", -1)])
			try:
				cat_id = collection['category_id'];
				cat_id = cat_id.replace("CAT","")
			except:
				cat_id = "0";
			cat={}
			category_id = "CAT" + (str(int(cat_id) +1)).zfill(4)
			cat['category_id'] = "CAT" + (str(int(cat_id) +1)).zfill(4)
			cat['category_name'] = category_name
			cat['created_at']=(datetime.now())
			cat['add_by']=manager_id
			db.categories.insert(cat)
		else:
			category_id = opts['category_id']
			
			
		#add Company
		
		if "company_id" not in opts:
			company_name = opts.get("company_name")
			collection = db.companies.find_one(sort=[("company_id", -1)])
			try:
				com_id = collection['company_id'];
				com_id = com_id.replace("COM","")
			except:
				com_id = "0";
			com={}
			company_id="COM" + (str(int(com_id) +1)).zfill(4)
			com['company_id'] = "COM" + (str(int(com_id) +1)).zfill(4)
			com['company_name'] = company_name
			com['created_at']=(datetime.now())
			com['add_by']=manager_id
			db.companies.insert(com)
		else:
			company_id=opts['company_id']
			
		
		#add Item 
		data = {}
		data['item_id']=item_id
		data['company_id']=company_id
		data['company_name']=opts['company_name']
		data['category_id']=category_id
		data['category_name']=opts['category_name']
		data['product_name']=opts['product_name']
		data['barcode']=opts['barcode']
		data['detail']=opts['detail']
		data['price']=opts['price']
		data['weight']=opts['weight']
		data['shelf_life']=opts['shelf_life']
		data['img']= list()
		data['add_by']=manager_id
		data['img']=["http://jlabs.co/no_image.png"]
		data['created_at']=(datetime.now())
		data['updated_at']=(datetime.now())
		db.inventory.insert(data);
		return basic_success({"item_id":item_id , "company_id":company_id , "category_id":category_id})
	except:
		return basic_error("Something went wrong!")