"""
Main indexer which creates the index for the offers
"""

import pprint
printer = pprint.PrettyPrinter(indent=3)
""" Algorithm
0. Find the offer_id of all offers that have an expiry ahead of current date
1.

"""

from datetime import datetime

from db_con import db

# --------- Step 1, complete each offer -------------

non_expired_offers = dict(
    (off['offer_id'], off) for off in
    db.offers_alt.find({
        "expiry": {"$gt": datetime.now()}
    }, {"_id": 0})
)

#print(non_expired_offers)

''' This will be a map of offer_id against offer with stats '''
offer_vendor_aggregate = dict(
    (off['offer_id'], off) for off in
    db.codes_alt.aggregate([
        {"$match": {
            "used": False,
            "offer_id": {"$in": list(non_expired_offers.keys())}
        }},
        {"$group": {
            "_id": {
                "vendor_id": "$vendor_id",
                "offer_id": "$offer_id"
            },
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gt": 0}}},
        {"$group": {
            "_id": "$_id.offer_id",
            "vendors": {
                "$addToSet": {
                    "vendor_id": "$_id.vendor_id",
                    "code_count": "$count"
                }
            }
        }},
        {"$project": {
            "offer_id": "$_id",
            "_id": 0, "vendors": 1
        }}
    ])
)


# Update the aggregation result with data from the offers collection
# note, we will update the vendor information of whether it delivers or not based on the location later
for offer_id, offer in offer_vendor_aggregate.items():
    offer.update(non_expired_offers[offer_id])
    # convert the vendors list into a dictionary
    vendors = offer.pop('vendors')
    v_dict = dict((v['vendor_id'], v['code_count']) for v in vendors)
    offer['vendors'] = v_dict

'''adding item data using method 2'''
item_ids = set(map(lambda off: off['item_id'], offer_vendor_aggregate.values()))
items_map = dict(
    (item['item_id'], item) for item in
    db.items_alt.find({"item_id": {"$in": list(item_ids)}}, {
        "_id": 0, "company_id": 0, "barcode": 0
    })
)


for offer in offer_vendor_aggregate.values():
    offer['item'] = items_map.get(offer.pop('item_id'))

# --- Now for some banner stuff -----
off_banners = dict()
ext_banners = []
for banner in db.banners.find({}, {"_id": False}):
    if banner['type'] == "offer":
        off_banners[banner['offer_id']] = banner
    else:
        ext_banners.append(banner)

# Now for the final push, creating the actual data
loc_data = list(db.index_location.find({}, {"_id": False}))
for item in loc_data:
    doc = {"new": True}
    doc.update(item)
    vendors = doc.pop('vendors')
    v_dict = dict((v['vendor_id'], v['delivery']) for v in vendors)
    doc['offers'] = []
    offer_ids = []
    doc['banners'] = ext_banners
    for offer in offer_vendor_aggregate.values():
        common_keys = v_dict.keys() & offer['vendors'].keys()
        if common_keys:
            apOffer = offer.copy()
            oVendors = apOffer.pop('vendors')
            f_vendors = []
            for key in common_keys:
                f_vendors.append({
                    "vendor_id": key,
                    "delivery": v_dict[key],
                    "code_count": oVendors[key]
                })
            apOffer['delivery'] = any(vendor['delivery'] for vendor in f_vendors)
            apOffer['vendors'] = f_vendors
            doc['offers'].append(apOffer)
            offer_ids.append(apOffer['offer_id'])

    if len(offer_ids):
        banners = []
        for oid in offer_ids:
            banner = off_banners.get(oid)
            if banner:
                banners.append(banner)

        doc['banners'] += banners
    db.index_offers.update_one({"area": doc['area'], "location": doc['location']}, {"$set": doc}, upsert=True)

db.index_offers.delete_many({"new": {"$exists": False}})
db.index_offers.update_many({}, {"$unset": {"new": ""}})
