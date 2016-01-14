"""
Create an index for the location against the vendors available there and their delivery types
"""
from .db_con import db

# change alt collection to actual
db.vendors_alt.aggregate([
    {"$unwind": "$op_locations"},
    {"group": {
        "_id": {
            "area": "$op_locations.area",
            "location": "$op_locations.location"
        },
        "vendors": {
            "$addToSet": {
                "vendor_id": "$vendor_id",
                "delivery": "$op_location.delivery"
            }
        }
    }},
    {"$project": {
        "_id": 0,
        "area": "$_id.area",
        "location": "$_id.location",
        "vendors": 1
    }},
    {"$out": "index_location"}
])
