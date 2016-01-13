__author__ = 'Pradeep'
from bson.json_util import dumps
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db,jsonResponse
import json

failure = dumps({"success":0})

@csrf_exempt
def activeRewards(request):
    # data = db.locations
    # result = data.find(projection={"_id":False})
    # success = dumps({"success": 1, "data": result, "totals": result.count()})
	return jsonResponse({"rewards":[{"offer_id":1,"title":"Redeem on Ola Cabs","img":"https://upload.wikimedia.org/wikipedia/en/9/94/Ola_Cabs_logo.png","points":20},{"offer_id":2,"title":"Redeem on Snapdeal","img":"https://pbs.twimg.com/profile_images/672841756702990336/xpVU8NQe_normal.png","points":30},{"offer_id":3,"title":"Redeem on FoodPanda","img":"https://lh3.googleusercontent.com/-ZMJdHaQ9qsk/AAAAAAAAAAI/AAAAAAAAAEQ/CclEWcAsopE/s46-c-k-no/photo.jpg","points":80},{"offer_id":4,"title":"Redeem on Flipkart","img":"https://www.indianbodybuilding.co.in/products/wp-content/uploads/thumbs_dir/Flipkart-Logo-mczpdcez7dns2l1cwsv3f7kkkzrkz4ngm6jw5c4ub8.png","points":70},{"offer_id":5,"title":"Redeem on Amazon","img":"https://lh3.googleusercontent.com/-c9bKgaRfC3Q/AAAAAAAAAAI/AAAAAAAAJUE/Eo2MLCqyiZs/s46-c-k-no/photo.jpg","points":100},{"offer_id":6,"title":"Redeem on Zimply","img":"http://cdn.slidesharecdn.com/profile-photo-Zimply_IN-96x96.jpg","points":120},{"offer_id":7,"title":"Redeem on Pepperfry","img":"https://lh3.googleusercontent.com/-JJ7GNcgX7uQ/AAAAAAAAAAI/AAAAAAAAIww/lpkWGwFsgSI/s46-c-k-no/photo.jpg","points":220},{"offer_id":8,"title":"Redeem on AliExpress","img":"http://www.baosell.com/image/rs-slider/slides/aliexpress_logo_3d.png","points":520},{"offer_id":9,"title":"Redeem on Jabong","img":"https://lh3.googleusercontent.com/-ghYZro2Wf0Q/AAAAAAAAAAI/AAAAAAAAOQ0/_l00yURG4Bs/s46-c-k-no/photo.jpg","points":220},{"offer_id":10,"title":"Redeem on Myntra","img":"http://images.vouchercodesuae.com/logos/64px/myntra.com-coupons-codes.png","points":250}],"history":[{"offer_id":1,"title":"Redeem on Ola Cabs","img":"https://upload.wikimedia.org/wikipedia/en/9/94/Ola_Cabs_logo.png","points":-20},{"offer_id":2,"title":"Redeem on Snapdeal","img":"https://pbs.twimg.com/profile_images/672841756702990336/xpVU8NQe_normal.png","points":-30},{"offer_id":3,"title":"Redeem on FoodPanda","img":"https://lh3.googleusercontent.com/-ZMJdHaQ9qsk/AAAAAAAAAAI/AAAAAAAAAEQ/CclEWcAsopE/s46-c-k-no/photo.jpg","points":-80},{"offer_id":4,"title":"Redeem on Flipkart","img":"https://www.indianbodybuilding.co.in/products/wp-content/uploads/thumbs_dir/Flipkart-Logo-mczpdcez7dns2l1cwsv3f7kkkzrkz4ngm6jw5c4ub8.png","points":-70},{"offer_id":5,"title":"Redeem on Amazon","img":"https://lh3.googleusercontent.com/-c9bKgaRfC3Q/AAAAAAAAAAI/AAAAAAAAJUE/Eo2MLCqyiZs/s46-c-k-no/photo.jpg","points":-100},{"offer_id":6,"title":"Redeem on Zimply","img":"http://cdn.slidesharecdn.com/profile-photo-Zimply_IN-96x96.jpg","points":-120},{"offer_id":7,"title":"Redeem on Pepperfry","img":"https://lh3.googleusercontent.com/-JJ7GNcgX7uQ/AAAAAAAAAAI/AAAAAAAAIww/lpkWGwFsgSI/s46-c-k-no/photo.jpg","points":-220},{"offer_id":8,"title":"Redeem on AliExpress","img":"http://www.baosell.com/image/rs-slider/slides/aliexpress_logo_3d.png","points":-520},{"offer_id":9,"title":"Redeem on Jabong","img":"https://lh3.googleusercontent.com/-ghYZro2Wf0Q/AAAAAAAAAAI/AAAAAAAAOQ0/_l00yURG4Bs/s46-c-k-no/photo.jpg","points":-220},{"offer_id":10,"title":"Redeem on Myntra","img":"http://images.vouchercodesuae.com/logos/64px/myntra.com-coupons-codes.png","points":-250}],"earning":[{"offer_id":1,"title":"Colgate Tooth Paste 500gm","points":20},{"offer_id":2,"title":"Coca cola 1L","points":30},{"offer_id":3,"title":"Maggi 250gm","points":80},{"offer_id":4,"title":"M.D.H 1KG","points":70},{"offer_id":5,"title":"Fortune Oil 2L","points":100},{"offer_id":6,"title":"Lifebuoy 150gm","points":120}],"extra":[{"total_rewards":10,"total_earning":5273,"total_redeemed":1234,"total_balance":4039}],"success":1})
'''def rewardHistory(request):
    data = db.locations
    try:
        area = request.GET['area']
    except:
        return HttpResponse(failure, content_type="application/json")
    query = {"area":area}
    result = data.find(query, {"_id":False,"locations": True})
    success = dumps({"success": 1, "data": result['data'][0]['location'], "total": result.count()})
    return HttpResponse(success, content_type="application/json")'''