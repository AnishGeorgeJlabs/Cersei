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
for banner in db.banners.find():
    if banner['type'] == "offer":
        off_banners[banner['offer_id']] = banner
    else:
        ext_banners.append(banner)

# Now for the final push, creating the actual data
loc_data = list(db.index_location.find())
for doc in loc_data:
    vendors = doc.pop('vendors')
    v_dict = dict((v['vendor_id'], v['delivery']) for v in vendors)
    doc['vendors'] = v_dict
    doc['offers'] = []
    offer_ids = []
    if len(ext_banners):
        doc['external_banners'] = ext_banners
    for offer in offer_vendor_aggregate.values():
        common_keys = doc['vendors'].keys() & offer['vendors'].keys()
        if common_keys:
            apOffer = offer.copy()
            oVendors = apOffer.pop('vendors')
            f_vendors = []
            for key in common_keys:
                f_vendors.append({
                    "vendor_id": key,
                    "delivery": doc['vendors'][key],
                    "code_count": oVendors[key]
                })
            apOffer['vendors'] = f_vendors
            doc['offers'].append(apOffer)
            offer_ids.append(apOffer['offer_id'])
    doc.pop('vendors')

    if len(offer_ids):
        banners = []
        for oid in offer_ids:
            banner = off_banners.get(oid)
            if banner:
                banners.append(banner)

        doc['offer_banners'] = banners

loc_data = list(filter(lambda d: len(d['offers']) > 0, loc_data))


printer.pprint(loc_data)

# AND WE WILL NOW ADD THIS TO DATABASE
'''
try:
    db.index_offers.delete()
except:
    pass
db.index_offers.insert_many(loc_data)
'''
