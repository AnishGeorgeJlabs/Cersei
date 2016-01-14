"""
Main indexer which creates the index for the offers
"""
""" Algorithm
0. Find the offer_id of all offers that have an expiry ahead of current date
1.

"""

from datetime import datetime

from cache import Cache
from db_con import db

# --------- Step 1, complete each offer -------------
item_cache = Cache("item")

non_expired_offers = list(map(
    lambda offer: offer['offer_id'],
    db.offers_alt.find({
        "expiry": {"$gt": datetime.now()}
    }, {"offer_id": 1, "_id": 0})
))

print(non_expired_offers)

offer_vendor_aggregate = list(
    db.codes_alt.aggregate([
        {"$match": {
            "used": False,
            "offer_id": {"$in": non_expired_offers}
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
        }}
    ])
)

print(offer_vendor_aggregate)
