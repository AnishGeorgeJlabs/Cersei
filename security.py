from django.views.decorators.csrf import csrf_exempt

from bson.json_util import ObjectId
from . import db, get_json, basic_failure, basic_error, basic_success

collection_map = {
    "user": "users",
    "vendor": "vendors",
    "fe": "fe"
}
@csrf_exempt
def login(request):
    """
    Universal login procedure
    :param request:
    :return:
    """
    data = get_json(request)
    for key in ['username', 'password', 'type']:
        if key not in data:
            return basic_error(key+" missing")

    user_key = data['type'] + "_id"         # can be vendor_id, fe_id, user_id

    res = db.credentials.find_one({"username": data['username'], "password": data['password']})
    if res:
        c_id = int(res[user_key])
        user = db.get_collection(collection_map[data['type']]).find_one({user_key: c_id})
        return basic_success({
            user_key: c_id,
            "api_key": str(res['_id']),
            "name": user['name'],
            "address": user.get('address')
        })
    else:
        return basic_failure("Unauthorized access")

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
    type = opts['type']
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

        for key in ['api_key', 'vendor_id']:
            if key not in opts:
                return basic_error(key+" missing, unauthorized access")

        api_key = opts.get('api_key')
        vendor_id = int(opts.get('vendor_id'))
        try:
            if db.credentials.count({"_id": ObjectId(api_key), "vendor_id": vendor_id}) > 0:
                return handler(opts, vendor_id, request.method)
            else:
                return basic_failure("Unauthorized access")
        except Exception as e:
            return basic_error("Handler error: "+str(e))

    return authorized_access
