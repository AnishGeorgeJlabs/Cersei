__author__ = 'Gopal'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse,basic_success,basic_failure,basic_error ,get_json
import json
import calendar
from datetime import datetime
failure = dumps({"success": 0})

@csrf_exempt
def list_item(request):
	try:
		fe_id = request.GET['fe_id']
		
	except:
		return basic_failure("Inavalid key parameters")
	try:
		data=db.fe_db
		fe = data.find_one({"fe_id":int(fe_id)} , {"_id":False})
		if not fe:
			return basic_failure("Not found")
		company_id = fe['company_id']
		data=db.items_alt
		result=data.find({"company_id":{"$in":company_id}} , {"_id":False})
		return basic_success(result)
	except:
		return basic_failure()
@csrf_exempt
def list_vendor(request):
	try:
		fe_id = request.GET['fe_id']
		
	except:
		return basic_failure("Inavalid key parameters")
	try:
		data=db.fe_db
		fe = data.find_one({"fe_id":int(fe_id)} , {"_id":False})
		if not fe:
			return basic_failure("Not found")
		mystores = fe['my_store']	
		data=db.vendors_alt
		result=data.find(projection={"_id":False , "vendor_id":1 , "name":1 , "address.address":1})
		return basic_success({"stores":result , "mystore":mystores})
	except:
		return basic_failure()
@csrf_exempt
def list_offers(request):
	try:
		try:
			fe_id = request.GET['fe_id']
		except:
			return basic_failure("Inavalid key parameters")
		data=db.fe_db
		fe = data.find_one({"fe_id":int(fe_id)} , {"_id":False})
		if not fe:
			return basic_failure("Not found")
		company_id = fe['company_id']
		data=db.items_alt
		result=data.find({"company_id":{"$in":company_id}} , {"_id":False})
		items_id=list()
		for res in result:
			items_id.append(res['item_id'])
		data=db.codes_alt
		result=list(data.aggregate( [
			{
				"$match":{
					"used":False
				}
			},
			{ 
				'$group':{
					'_id':"$offer_id" ,
					"vendors":{
						'$addToSet':"$vendor_id"
					},
					"count": {"$sum": 1}
				}
			},
			{
				"$project": {
					"offer_id": "$_id",
					"_id": 0 , "count":1 , "vendors":1
				}
			}
		]))
		data=db.offers_alt
		aa = list(data.aggregate([
			{
			   "$match":{
					"expired":False , 
					"item_id":{
						"$in":items_id}
				}
			},
			{
				'$project': {
				  'DM': { '$dateToString': { 'format': "%Y/%m", 'date': "$dom" } },
				  'DE': { '$dateToString': { 'format': "%Y/%m", 'date': "$expiry" } },
				  "_id":0,
				  "offer_id":1 , "points":1 , 'item_id':1 
			   }
			 }
		   ]
		))
		result1=list()
		for r in aa:
			for res in result: 
				if r['offer_id']==res['offer_id']:
					r['vendors']=res['vendors']
					result1.append(r)
		return basic_success(result1)
	except:
		return basic_failure()
@csrf_exempt
def create_offers(request):
	
	data=db.offers_alt
	max1 = max(list(data.distinct("offer_id")))
	codes=list()
	try:
		dt=get_json(request)
		fe_id=dt['fe_id']
		new_offer=dt['new_offer']
		old_offer=dt['old_offer']
		total_offer=dt['count']
		dataa=list()
		countt=0
		all_offers_id=list()
		for new in new_offer:
			DOM = (new['dom']).split("-")
			day = calendar.monthrange(int(str(DOM[0])) , int(str(DOM[1])))[1]
			DM=datetime.strptime(new['dom']+"-"+str(day) , "%Y-%m-%d")
			DOE = (new['doe']).split("-")
			day = calendar.monthrange(int(str(DOE[0])) , int(str(DOE[1])))[1]
			DE=datetime.strptime(new['doe']+"-"+str(day) , "%Y-%m-%d")
			item_id=new['item_id']
			v_id=new['vendors']
			points=new['points']
			vendor_list = list()
			offer_id = max1
			max1=max1+1;
			code={}
			for v in v_id:
				vendor_list.append(v['vid'])
				for cd in v['qrcodes']:
					code['used']=False
					code['vendor_id']=v['vid']
					code['codes']=cd
					code['offer_id']=max1
					codes.append(code.copy())
			result=data.insert({"offer_id":max1 , "dom":DM , "expiry":DE , "points":int(points) , "fe_id":[ fe_id] , "item_id":item_id , "vendor_id":vendor_list , "expired":False})
			all_offers_id.append(max1)
			countt+=1
		for old in old_offer:
			vid=old['vendors']
			offer_id=old['offer_id']
			vendor_list = list()
			code={}
			for v in vid:
				vendor_list.append(v['vid'])
				for cd in v['qrcodes']:
					code['used']=False
					code['vendor_id']=v['vid']
					code['codes']=cd
					code['offer_id']=offer_id
					codes.append(code.copy())
			result = data.find_one_and_update({"offer_id":offer_id} ,{	"$addToSet":{"fe_id":fe_id,"vendor_id":{"$each":vendor_list}	}})
			all_offers_id.append(offer_id)
			countt+=1
		data=db.codes_alt
		result = data.insert_many(codes)
		data=db.fe_db
		result = data.find_one_and_update({"fe_id":int(fe_id)} , {"$addToSet":{"my_offer":{"$each":all_offers_id}}})
		return basic_success(countt)
	except Exception as e:
		return basic_failure(str(e))
	
		
	
		