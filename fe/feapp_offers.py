__author__ = 'Gopal'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
import os , sys
from . import db,jsonResponse,basic_success,basic_failure,basic_error ,get_json
import json
from datetime import datetime , date , timedelta
import calendar
from datetime import date
failure = dumps({"success": 0})

@csrf_exempt
def list_item(opts , fe_id , method):
	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		if not fe:
			return basic_failure("Not found")
		company_id = fe['company_id']
		data=db.inventory
		result=data.find({"company_id":company_id} , {"_id":False})
		return basic_success(result)
	except:
		return basic_failure()
	

	
@csrf_exempt
def list_retailer(opts , fe_id , method):
	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		if not fe:
			return basic_failure("Not found")
		mystores = fe['my_stores']	
		data=db.retailer
		result=data.find(projection={"_id":False, "retailer_id":1 , "name":1 , "address":1})
		return basic_success({"stores":result , "mystore":mystores})
	except:
		return basic_failure()

@csrf_exempt
def list_qrcodes(opts , fe_id , method):
	try:
		if opts.get("offer_id"):
			result=db.qrcodes.aggregate([
				{
					'$match':{
						"offer_id":opts.get("offer_id")
					}
				},
				{
					'$group':{
						'_id':'$used' ,
						'qrcodes':{'$push':'$qrcodes'}
					}
				}
			])
			data={}
			data['used']=list()
			data['unused']=list()
			if result:
				for r in result:
					if r['_id'] is True:
						data['used']=r['qrcodes']
					if  r['_id'] is False:
						data['unused']=r['qrcodes']
				return basic_success(data)
			else:
				return basic_failure("Offer not found")
		else:
			return basic_failure("Offer ID missing")
	except Exception as e:
		return basic_error("Something went wrong")



@csrf_exempt
def list_offers(opts , fe_id , method):

	try:
		data=db.FE
		fe = data.find_one({"fe_id":(fe_id)} , {"_id":False})
		if not fe:
			return basic_failure("Not found")
		items_result = db.inventory.find({'company_id':fe['company_id']} , {"_id":0 , "item_id":1})
		items = list();
		if items_result:
			for item in items_result:
				items.append(item['item_id'])
		data = db.offers
		if fe['level'] is 1:
			offer_result = data.find({"fe_id":{'$in':fe['fe'] },"deleted_at":{'$exists':False} , "item_id":{'$in':items}} , {"_id":False})
		else:
			offer_result = data.find({"fe_id":fe_id,"deleted_at":{'$exists':False}, "item_id":{'$in':items}} , {"_id":False})
		data=db.qrcodes
		codes=list(data.aggregate( [
			{
				"$match":{
					"used":False
				}
			},
			{ 
				'$group':{
					'_id':"$offer_id" ,
					"count": {"$sum": 1}
				}
			},
			{
				"$project": {
					"offer_id": "$_id",
					"_id": 0 , "count":1 
				}
			}
		]))
		temp = db.qrcodes.find({'qrcode':{'$exists':True }  ,'offer_id':{'$exists':True}},{'_id' :False });
		total_count={}
		for t in temp:
			 try:
			 	total_count[t['offer_id']] +=1
			 except:
			 	total_count[t['offer_id']] = 1 	
		
		offer_data=list();
		for offer_res in offer_result:
			offer_res.update({'remaining_codes':0})
			offer_res.update({'total_codes':0})
			offer_res['dom']=(offer_res['dom']).strftime("%d/%m/%Y")
			offer_res['expired_on']=(offer_res['expired_on']).strftime("%d/%m/%Y")
			offer_data.append(offer_res)
		for offer_res in offer_data:
			for code in codes:
				if code['offer_id'] == offer_res['offer_id']:
					offer_res['remaining_codes']=code['count']
					if total_count.get(code['offer_id']):
						offer_res['total_codes']=total_count[code['offer_id']]

		return basic_success(offer_data)
	except Exception as e:
		return basic_failure(str(e))

@csrf_exempt
def create_offers(opts , fe_id , method):
	
	collection = db.offers.find_one(sort=[("offer_id", -1)])
	try:
		id = collection['offer_id'];
		id = id.replace("OF","")
	except:
		id = "0";
	pid = int(id)
	try:
		new_offer=opts['new_offer']
		old_offer=opts['old_offer']
		count=0
		data={}
		data1={}
		data1['new_offer'] = list()
		data1['old_offer'] = list()
		data['new_offer'] = list()
		data['old_offer'] = list()
		codes=list()
		all_offers_id=list()
		for new in new_offer:
			temp={}
			temp['offer_id'] = "OF" + (str((pid) +1)).zfill(4)
			temp['retailer_id'] = new['vid']
			temp['retailer_name'] = new['name']
			temp['fe_id'] = fe_id
			temp['approved']= False
			temp['item_id']=new['item_id']
			temp['cashback']=new['cashback']
			temp['created_at']=(datetime.now() + timedelta(hours=5,minutes=30))
			temp['updated_at']=(datetime.now() + timedelta(hours=5,minutes=30))
			temp['dom'] = datetime.strptime(new['dom'], "%Y-%m-%d")
			temp['expired_on'] = temp['dom'] + timedelta(days=int(new['shelf_life']))
			pid+=1
			all_offers_id.append(temp['offer_id'])
			for x in new['qrcodes']:
				code={}
				code['used']=False
				code['status']="live"
				code['retailer_id']=new['vid']
				code['qrcodes']=x
				code['offer_id']=temp['offer_id']
				code['item_id']=new['item_id']
				code['created_at']=(datetime.now() + timedelta(hours=5,minutes=30))
				codes.append(code.copy())
				count+=1
			(data['new_offer']).append(temp.copy())
			(data1['new_offer']).append(new['offer_id'])
			
		for old in old_offer:
			offer_id=old['offer_id']
			for x in old['qrcodes']:
				code={}
				code['used']=False
				code['status']="live"
				code['retailer_id']=old['vid']
				code['qrcodes']=x
				code['offer_id']=offer_id
				code['item_id']=old['item_id']
				code['created_at']=(datetime.now() + timedelta(hours=5,minutes=30))
				codes.append(code.copy())
				count+=1
			
			expired_on = datetime.strptime(old['dom'], "%Y-%m-%d") + timedelta(days=int(old['shelf_life']))
			result = db.offers.find_one_and_update({"offer_id":offer_id} ,{	 '$set':{"updated_at":datetime.now()  + timedelta(hours=5,minutes=30)  , "cashback":int(old['cashback']) , "dom":datetime.strptime(old['dom'], "%Y-%m-%d") , "expired_on":expired_on , "updated_by":fe_id}})
			(data1['old_offer']).append(offer_id)
		if len(data['new_offer']):
			result_n = db.offers.insert_many(data['new_offer'])
		if len(codes):
			result_c = db.qrcodes.insert_many(codes)
		result = db.FE.find_one_and_update({"fe_id":(fe_id)} , {"$addToSet":{"my_offer":{"$each":all_offers_id}}})
		data1['codes_count']=count
		return basic_success(data1)
	except Exception as e:
		'''exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		return basic_error([exc_type, fname, exc_tb.tb_lineno , str(e)])'''
		return basic_error(str(e))
		
@csrf_exempt
def delete_offers(opts , fe_id , method):
	try:
		if opts.get("offer_id"):
			result = db.offers.update_one({"offer_id":opts.get("offer_id")} ,{	 '$set':{"deleted_at":datetime.now()  + timedelta(hours=5,minutes=30)  , "deleted_by":fe_id}} )
			if result.modified_count:
				return basic_success("Offer Deleted")
			else:
				return basic_failure("Offer not found")
		else:
			return basic_failure("Offer ID missing")
	except Exception as e:
		return basic_error("Something went wrong")



@csrf_exempt
def edit_offer(opts , fe_id , method):
	try:
		offer_id = opts['offer_id']
		cb = opts['cashback']
		result = db.offers.update_one({"offer_id":opts.get("offer_id")} ,{	 '$set':{"updated_at":datetime.now()  + timedelta(hours=5,minutes=30)  , "cashback":cb , "updated_by":fe_id , 'approved':False}} )
		if result.modified_count:
			return basic_success({"msg":'Offer Updated and waiting for approval' , "offer_id" :offer_id})
		else:
			return basic_failure("Offer not found")
	except Exception as e:
		return basic_error("Something went wrong")
