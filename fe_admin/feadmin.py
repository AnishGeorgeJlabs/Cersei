__author__ = 'Gopal'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
import os , sys
from pymongo import ReturnDocument
from . import db,jsonResponse,basic_success,basic_failure,basic_error ,get_json
import json
from datetime import datetime , date , timedelta
import calendar
from datetime import date
failure = dumps({"success": 0})

@csrf_exempt
def create_feuser(opts , fe_id , method):
	# ------- Add new FE User ----------
	try:
		if method != 'POST':
			return basic_error("POST Method only");
		for key in ['name' , "contact" ,'email', 'password' , 'username']:
			if key not in opts:
				return basic_error(key+" missing")
		fe_exist= db.credentials.find_one({"username" :opts['username']})
		if fe_exist:
			return basic_error("Username already in use. Please choose another username")
		feresult= db.FE.find_one({"fe_id" :fe_id})		
		if not feresult or feresult['level'] is not 1:
			return basic_failure("Unknown FE Admin")
		result = db.FE.find_one({'level':0}  , sort=[("fe", -1)])
		try:
			fe = result['fe_id'];
			fe = fe.replace("FE","")
		except:
			fe = "0";
		fe = "FE" + (str(int(fe) +1)).zfill(4)
		data = {}
		data['fe_id']=fe
		data['name']=opts['name']
		data['contact']=opts['contact']
		data['email_id']=opts['email']
		data['company_id']=feresult['company_id']
		data['my_offer']=list()
		data['my_stores']=list()
		data['level']=0
		data['add_by']=fe_id
		data['created_at']=(datetime.now())
		data['updated_at']=(datetime.now())
		result = db.FE.insert(data);
		data= {}
		data['username']=opts['username']
		data['password']=opts['password']
		data['fe_id']=fe
		data['type']="fe"
		data['created_at']=(datetime.now())
		data['updated_at']=(datetime.now())
		db.FE.update_one({"fe_id":fe_id} , {'$addToSet':{'fe':fe}})
		result = db.credentials.insert(data);
		return basic_success(fe)
	except:
		return basic_error("Something went wrong!")
		'''exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		return basic_error([exc_type, fname, exc_tb.tb_lineno , str(e)])'''
		
	
@csrf_exempt
def list_fe(opts , fe_id , method):
	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		if not fe or fe['level'] is not 1:
			return basic_failure("Unknown FE Admin")
		
		result=db.FE.find({"company_id":fe['company_id'] , "level":0} , {"_id":False})
		return basic_success(result)
	except:
		return basic_failure("Something went wrong!")

@csrf_exempt
def remove_fe(opts , fe_id , method):
	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		if not fe or fe['level'] is not 1:
			return basic_failure("Unknown FE Admin")
		if opts.get('remove_id'):	
			result = db.FE.delete_one({'fe_id': opts.get('remove_id') , 'level':0})
			result = db.credentials.delete_one({'fe_id': opts.get('remove_id') , "type":"fe"})
			if result.deleted_count is 1:
				return basic_success("FE User Removed")
			else:
				return basic_error("FE not found")
		else:
			return basic_error("FE ID missing")
	except:
		return basic_error("Something went Wrong")	

@csrf_exempt
def approve_offer(opts , fe_id , method):
	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		if not fe or fe['level'] is not 1:
			return basic_failure("Unknown FE Admin")
		if opts.get('offer_id'):
			r = db.offers.find_one({'offer_id': opts.get('offer_id')})
			if r and r.get('new_cashback'):
				result=db.offers.find_one_and_update({'offer_id': opts.get('offer_id')},{'$set': {'approved': True , 'cashback':int(r.get('new_cashback'))} , '$unset':{"new_cashback":""}},projection={'approved': True, '_id': False},return_document=ReturnDocument.AFTER)
			else:
				result=db.offers.find_one_and_update({'offer_id': opts.get('offer_id')},{'$set': {'approved': True }},projection={'approved': True, '_id': False},return_document=ReturnDocument.AFTER)
			if result['approved'] is True:
				return basic_success("Offer approved")
			else:
				return basic_error("offer not found")
		else:
			return basic_error("offer ID missing")
	except Exception as e:
		return basic_error(str(e)+"Something went Wrong")	

@csrf_exempt
def send_message(opts , fe_id , method):
	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		if not fe or fe['level'] is not 1:
			return basic_failure("Unknown FE Admin")
		if opts.get('message'):	
			msg = {}
			msg['timestamp']=(datetime.now() + timedelta(hours=5,minutes=30))
			msg['msg']=opts.get('message')
			db.FE.find_one_and_update({'fe_id': fe_id},{'$addToSet': {'messages': msg}})
			return basic_success("Message sent")
		else:
			return basic_error("Message Missing")
	except:
		return basic_error("Something went Wrong")	

@csrf_exempt
def show_messages(opts , fe_id , method):
	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		result = data.find({"level":1 , "company_id":fe['company_id'] } , {"_id":0 , "messages":1})
		if result:
			return basic_success(result)
		else:
			return basic_error("messages not found")
	except:
		return basic_error("Something went Wrong")		
