__author__ = 'Gopal'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse,basic_success,basic_failure,basic_error ,get_json
import json
from datetime import datetime
import calendar
from datetime import date
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
		data = db.offers_alt
		offer_result = data.find({"fe_id":int(fe_id)} , {"_id":False})
		data=db.codes_alt
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
		
		offer_data=list();
		for offer_res in offer_result:
			offer_res.update({'remaining_codes':0})
			offer_res['dom']=(offer_res['dom']).strftime("%d/%m/%Y")
			offer_res['created_on']=(offer_res['created_on']).strftime("%d/%m/%Y")
			offer_res['expiry']=(offer_res['expiry']).strftime("%d/%m/%Y")
			offer_data.append(offer_res)
		for offer_res in offer_data:
			for code in codes:
				if code['offer_id'] is offer_res['offer_id']:
					offer_res['remaining_codes']=code['count']
		return basic_success(offer_data)
		'''company_id = fe['company_id']
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
					"vendors":"$vendor_id"
					,
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
				  'approved':"$approved",
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
		return basic_success(result1)'''
		
	except Exception as e:
		return basic_failure(str(e))
@csrf_exempt
def create_offers(request):
	
	data=db.offers_alt
	max1 = max(list(data.distinct("offer_id")))
	codes=list()
	try:
		dt=get_json(request)
		if(dt['fe_id']):
			fe_id=dt['fe_id']
		else:
			return basic_failure()
		new_offer=dt['new_offer']
		old_offer=dt['old_offer']
		countt=0
		data1={}
		data1['new_offer'] = list()
		data1['old_offer'] = list()
		for new in new_offer:
			dom = [int(n) for n in (new['dom']).split("-")]
			DOM = date(dom[0] , dom[1] , dom[2])
			total_month = int(new['shelf_life'])+dom[1]
			dom[0] = dom[0]+int(total_month/12)
			dom[1] = total_month%12
			try:
				DOE=date(dom[0] , dom[1],dom[2])
			except:
				p = calendar.monthrange(dom[0] , dom[1])
				DOE=date(dom[0] , dom[1],p[1])
			item_id=new['item_id']
			v_id=new['vendors']
			points=new['points']
			vendor_list = list()
			offer_id = max1
			max1=max1+1;
			all_offers_id = list()
			code={}
			for v in v_id:
				vendor_list.append(v['vid'])
				for cd in v['qrcodes']:
					code['used']=False
					code['vendor_id']=v['vid']
					code['codes']=cd
					code['offer_id']=max1
					codes.append(code.copy())
			result=data.insert({"offer_id":max1 , "dom":datetime.combine(DOM, datetime.min.time()) , "expiry":datetime.combine(DOE, datetime.min.time()) , "points":int(points) , "fe_id":[ fe_id] , "item_id":item_id , "vendor_id":vendor_list , "expired":False})
			(data1['new_offer']).append(new['offer_id'])
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
			(data1['old_offer']).append(offer_id)
			all_offers_id.append(offer_id)
			countt+=1
		data=db.codes_alt
		result = data.insert_many(codes)
		data=db.fe_db
		result = data.find_one_and_update({"fe_id":int(fe_id)} , {"$addToSet":{"my_offer":{"$each":all_offers_id}}})
		data1['count']=countt
		return basic_success(data1)
	except Exception as e:
		return basic_success(data1)
	
		
	
		