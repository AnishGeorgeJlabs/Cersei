from . import basic_success, basic_failure, basic_error, db

def order_list(opts, vendor_id, method):
    if method != "GET":
        return basic_failure("GET method only")

    # Get the status required
    status = opts.get("status", "placed")

    # Data fetch from db
    data = list(db.orders.aggregate([
        {"$match": {
            "vendor_id": vendor_id,
            "status.0.status": status
        }},
        {"$sort": {"timestamp": -1}},
        {"$project": {
            "_id": 0,
            "order_id": 1,
            "status": "$status.status",
            "address": 1,
            "timestamp": 1,
            "order.qty": 1,
            "order.price": 1
        }}
    ]))

    # Transform the data to get the price and stuff, todo: debatable
    for record in data:
        record['status'] = record['status'][0]
        order = record.pop('order')
        record['price'] = 0
        record['item_count'] = 0
        for item in order:
            record['price'] += item['price']
            record['item_count'] += item['qty']

    return basic_success(data)


def update_order(opts, vendor_id, method):
    if method != "POST":
        return basic_failure("POST method only")

    status = opts['status']
