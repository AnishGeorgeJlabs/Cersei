from django.views.decorators.csrf import csrf_exempt
import random
import string
from bson.json_util import ObjectId
from . import db, get_json, basic_failure, basic_error, basic_success
from datetime import date,datetime , timedelta
collection_map = {
	"user": "users",
	"vendor": "vendors",
	"fe": "fe_db",
	"manager":"manager"
}
@csrf_exempt
def login(request):
	"""
	Universal login procedure
	:param request:
	:return:
	"""
	data = get_json(request)
	for key in ['username', 'password', 'user_type']:
		if key not in data:
			return basic_error(key+" missing")

	user_key = data['user_type'] + "_id"         # can be vendor_id, fe_id, user_id

	res = db.credentials.find_one({"username": data['username'], "password": data['password']})
	if res:
		c_id = int(res[user_key])
		user = db.get_collection(collection_map[data['user_type']]).find_one({user_key: c_id})
		return basic_success({
			user_key: c_id,
			"api_key": str(res['_id']),
			"name": user['name'],
			"address": user.get('address')
		})
	else:
		return basic_failure("Unauthorized access")

@csrf_exempt
def m_login(request):
	"""
	Universal login procedure
	:param request:
	:return:
	"""
	data = get_json(request)
	for key in ['username', 'password', 'user_type']:
		if key not in data:
			return basic_error(key+" missing")

	user_key = data['user_type'] + "_id"         # can be vendor_id, fe_id, user_id

	res = db.credentials.find_one({"username": data['username'], "password": data['password']})
	if res:
		c_id = (res[user_key])
		user = db.get_collection(collection_map[data['user_type']]).find_one({user_key: c_id})
		return basic_success({
			user_key: c_id,
			"api_key": str(res['_id']),
			"name": user['name'],
			"address": user.get('address')
		})
	else:
		return basic_failure("Unauthorized access")


@csrf_exempt
def fe_login(request):
	"""
	FE Login  
	"""
	try:
		data = get_json(request)
		api_key =''.join(random.choice(string.ascii_uppercase +string.ascii_lowercase+'!@#$%^&*()' + string.digits) for _ in range(32))
		for key in ['username', 'password', 'user_type']:
			if key not in data:
				return basic_error(key+" missing")
		m=db.credentials.find_one({"username":data['username'] , "type":{'$in':['fe' , 'feadmin']}})
		if db.credentials.count({"username":data['username']}) > 0:
			if m['password'] == data['password']:
				fe_user = db.FE.find_one({"fe_id": m['fe_id']} , {"_id":False})
				result = db.credentials.update_one({"username":data['username'] , "type":m['type']} ,{'$set':{"api_key":api_key,"last_login":datetime.now() + timedelta(hours=5,minutes=30)}} )
				if result.modified_count:
					fe_user['api_key'] = api_key
					fe_user['type']=m['type']
					return basic_success(fe_user)
				else:
					return basic_error("Something went wrong. Please try later12.")
			else:
				return basic_error("Invalid Username And Password.")
		else:
			return basic_error("Invalid Username And Password.") 
	except Exception as e:
		return basic_error(str(e)+"Something went wrong. Please try later1.")

@csrf_exempt
def fake_login(request):    
	return basic_success({
		"vendor_id": 0,
		"api_key": "2e3ax301eskq5r32zxd205r",
		"name": "Mock vendor you know",
		"address": "Mock location for vendor"
	})

@csrf_exempt
def change_password(request):
	"""
	Universal change password controller
	:param request:
	:return:
	"""
	opts = get_json(request)
	type = opts['user_type']
	user_key = type + '_id'

	for key in ['api_key', user_key, 'old_pass', 'new_pass', 'username']:
		if key not in opts:
			return basic_error(key+" missing, unauthorized access")

	update = db.credentials.update_one({
		"_id": ObjectId(opts['api_key']),
		"username": opts['username'],
		"password": opts['old_pass'],
		"type": type,
		user_key: opts[user_key]
	}, {"$set": {"password": opts['new_pass']}})
	return basic_success(update.modified_count == 1)


def m_auth(handler):
	""" Authorization layer for merchant application
	:param handler: A function which will take 2 parameters (options, vendor_id) and return JSON response
	:return: the handler function wrapped with the authorization middleware
	"""
	@csrf_exempt
	def authorized_access(request):
		if request.method == "GET":
			opts = request.GET.copy()
		else:
			opts = get_json(request)

		user_key = opts['user_type'] + '_id'
		for key in ['api_key', user_key]:
			if key not in opts:
				return basic_error(key+" missing, unauthorized access")

		api_key = opts.get('api_key')
		c_id = (opts.get(user_key))
		try:
			if db.credentials.count({"_id": ObjectId(api_key), user_key: c_id}) > 0:
				return handler(opts, c_id, request.method)
			else:
				return basic_failure("Unauthorized access")
		except Exception as e:
			return basic_error("Handler error: "+str(e))

	return authorized_access


def auth(handler):
	""" Authorization layer for merchant application
	:param handler: A function which will take 2 parameters (options, vendor_id) and return JSON response
	:return: the handler function wrapped with the authorization middleware
	"""
	@csrf_exempt
	def authorized_access(request):
		if request.method == "GET":
			opts = request.GET.copy()
		else:
			opts = get_json(request)

		user_key = opts['user_type'] + '_id'
		for key in ['api_key', user_key]:
			if key not in opts:
				return basic_error(key+" missing, unauthorized access")

		api_key = opts.get('api_key')
		c_id = int(opts.get(user_key))
		try:
			if db.credentials.count({"_id": ObjectId(api_key), user_key: c_id}) > 0:
				return handler(opts, c_id, request.method)
			else:
				return basic_failure("Unauthorized access")
		except Exception as e:
			return basic_error("Handler error: "+str(e))

	return authorized_access

@csrf_exempt
def fe_auth(handler):
	""" Authorization layer for FE application
	:param handler: A function which will take 2 parameters (options, vendor_id) and return JSON response
	:return: the handler function wrapped with the authorization middleware
	"""
	@csrf_exempt
	def authorized_access(request):
		if request.method == "GET":
			opts = data.copy()
		else:
			opts = get_json(request)
		for key in ['api_key' , 'fe_id']:
			if key not in opts:
				return basic_error(key+" missing, unauthorized access")
		api_key = opts['api_key']
		fe_id = opts['fe_id']
		
		try:
			if db.credentials.count({"api_key": api_key, 'fe_id': fe_id}) > 0:
				return handler(opts, fe_id, request.method)
			else:
				return basic_failure("Unauthorized access")
		except Exception as e:
			return basic_error("Handler error: "+str(e))

	return authorized_access
