"""
    Api's for the retailer's account and all that stuff
"""
from . import db, basic_success, basic_failure, basic_error


def vendor_account(opts, vendor_id, method):
    # ------- vendor details ----------
    vendor = db.vendors.find_one({"vendor_id": vendor_id}, {"_id": False, "vendor_id": False})
    if not vendor:
        return basic_failure("Invalid vendor")

    # ------- account stats -----------
    vendor.update({
        "pending": 0,
        "cancelled": 0,
        "complete": 0,
        "total_points": 0
    })
    for item in db.orders.find({"vendor_id": vendor_id}, {"_id": False, "pts": True, "status": True}):
        status = item['status'][0]['status']

        if status == "placed":
            vendor['pending'] += 1
        elif status == "accepted":
            vendor['complete'] += 1
        else:
            vendor['cancelled'] += 1

        vendor['total_points'] += item.get('pts', 0)

    return basic_success(vendor)
