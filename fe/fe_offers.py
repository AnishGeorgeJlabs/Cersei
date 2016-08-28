__author__ = 'Gopal'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse,basic_success,basic_failure,basic_error ,get_json
import json
from datetime import datetime , date , timedelta
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
def login(request):
	m=db.credentials.find_one({"username":request.GET['username']})
	if db.credentials.count({"username":request.GET['username']}) > 0:
		if m['password'] == request.GET['password']:
			request.session['fe_id'] = m['fe_id']
			return basic_success(request.session.session_key )
		else:
			return basic_error("Invalid Username And Password.")
	else:
		return basic_error("Invalid Username And Password.")
		

def logout(request):
	try:
		del request.session['fe_id']
	except KeyError:
		pass
	return basic_success("You're logged out.")		
	
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
def list_vendor1(opts , id , method):
	try:
		data=db.fe_db
		fe = data.find_one({"fe_id":int(id)} , {"_id":False})
		if not fe:
			return basic_failure("Not found")
		mystores = fe['my_store']	
		data=db.vendors_alt
		result=data.find(projection={"_id":False , "vendor_id":1 , "name":1 , "address.address":1})
		return basic_success({"stores":result , "mystore":mystores })
	except Exception as e:
		return basic_failure(str(e))

@csrf_exempt
def list_offers(request):

	try:
		regex_http_          = re.compile(r'^HTTP_.+$')
		regex_content_type   = re.compile(r'^CONTENT_TYPE$')
		regex_content_length = re.compile(r'^CONTENT_LENGTH$')
		request_headers = {}
		for header in request.META:
			if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
				request_headers[header] = request.META[header]
		return basic_success([request.get_host() ,request_headers ])
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
		temp = db.codes_alt.find({'code':{'$exists':True }  ,'offer_id':{'$exists':True}},{'_id' :False });
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
			offer_res['created_on']=(offer_res['created_at']).strftime("%d/%m/%Y")
			offer_res['expiry']=(offer_res['expiry']).strftime("%d/%m/%Y")
			offer_data.append(offer_res)
		for offer_res in offer_data:
			for code in codes:
				if code['offer_id'] is offer_res['offer_id']:
					offer_res['remaining_codes']=code['count']
					if total_count.get(code['offer_id']):
						offer_res['total_codes']=total_count[code['offer_id']]

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
def create_offers(opts , fe_id , method):
	
	max1 = max(list(db.offers_alt.distinct("offer_id")))
	codes=list()
	try:
		new_offer=opts['new_offer']
		old_offer=opts['old_offer']
		count=0
		data={}
		data['new_offer'] = list()
		data['old_offer'] = list()
		for new in new_offer:
			dom = [int(n) for n in (new['dom']).split("-")]
			DM = date(dom[0] , dom[1] , dom[2])
			total_month = int(new['shelf_life'])+dom[1]
			d=dom
			dom[0] = dom[0]+int(total_month/12)
			dom[1] = total_month%12
			try:
				DE=date(dom[0] , dom[1],dom[2])
			except:
				p = calendar.monthrange(dom[0] , dom[1])
				DE=date(dom[0] , dom[1],p[1])
			item_id=new['item_id']
			v_id=new['vendors']
			points=new['points']
			vendor_list = list()
			max1=max1+1;
			offer_id = max1
			all_offers_id = list()
			code={}
			code['used']=False
			code['vendor_id']=v_id['vid']
			code['codes']=v_id['qrcodes']
			code['offer_id']=max1
			codes.append(code.copy())
			result=db.offers_alt.insert({"offer_id":max1 , "dom":datetime.combine(DM, datetime.min.time()) , "expiry":datetime.combine(DE, datetime.min.time()) ,"created_on":datetime.now() + timedelta(hours=5,minutes=30) ,  "points":int(points) , "fe_id":fe_id , "item_id":item_id , "vendor_id":v_id['vid'] , "expired":False , "approved":False})
			(data['new_offer']).append(new['offer_id'])
			all_offers_id.append(max1)
			count+=1
		for old in old_offer:
			offer_id=old['offer_id']
			code={}
			code['used']=False
			code['vendor_id']=old['vid']
			code['codes']=old['qrcodes']
			code['offer_id']=offer_id
			codes.append(code.copy())
			result = db.offers_alt.find_one_and_update({"offer_id":offer_id} ,{	 '$set':{"updated_at":datetime.now() + timedelta(hours=5,minutes=30)}})
			(data['old_offer']).append(offer_id)
			all_offers_id.append(offer_id)
			count+=1
		result = db.codes_alt.insert_many(codes)
		result = db.fe_db.find_one_and_update({"fe_id":int(fe_id)} , {"$addToSet":{"my_offer":{"$each":all_offers_id}}})
		data['count']=count
		return basic_success(data)
	except Exception as e:
		return basic_error(str(e))

