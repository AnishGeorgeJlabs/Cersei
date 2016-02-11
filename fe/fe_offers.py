__author__ = 'Gopal'
from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse,basic_success,basic_failure,basic_error
import json
from datetime import datetime
failure = dumps({"success": 0})

@csrf_exempt
def list_item(request):
	try:
		data=db.items_alt
		result=data.find(projection={"_id":False})
		return basic_success(result)
	except:
		return basic_failure()