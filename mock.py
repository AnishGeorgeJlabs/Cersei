from . import basic_success, basic_failure, db

details_map = {
    "order_1": {
        'name': 'Sumit',
        'phone': 8888888888,
        'address': '24/267, Agra Town, Chennai',
        'order_id': "order_1",
        'order': [
            {
                'name': 'Chavanprash',
                'id': 5,
                'qty': 1,
                'price': 100
            },
            {
                'name': 'Pepsodent',
                'id': 6,
                'qty': 2,
                'price': 20
            },
            {
                'name': 'Colgate',
                'id': 3,
                'qty': 1,
                'price': 10
            }
        ]
    },
    "order_2": {
        'name': 'Sumita',
        'phone': 8888888889,
        'address': '24/267, China Town, Delhi',
        'order_id': "order_2",
        'order': [
            {
                'name': 'Chavanprash',
                'id': 5,
                'qty': 1,
                'price': 100
            }
        ]
    },
    "order_3": {
        'name': 'Sid',
        'phone': 8188888888,
        'address': '23/267, Agra Palace, Mumbai',
        'order_id': "order_3",
        'order': [
            {
                'name': 'Chavanprash',
                'id': 5,
                'qty': 1,
                'price': 100
            },
            {
                'name': 'Colgate',
                'id': 3,
                'qty': 1,
                'price': 10
            }
        ]
    }
}


def details(request):
    order_id = request.GET.get("order_id", "order_#_1")
    if order_id not in details_map:
        return basic_failure('Not found')
    else:
        return basic_success(details_map[order_id])


def orders(request):
    orders_list = [
        {
            'address': '24/267, Agra Town, Chennai',
            'price': 130,
            'order_id': 'order_1',
            'item_count': 3
        },
        {
            'address': '24/267, China Town, Delhi',
            'price': 100,
            'order_id': 'order_2',
            'item_count': 1
        },
        {
            'address': '23/267, Agra Palace, Mumbai',
            'price': 110,
            'order_id': 'order_3',
            'item_count': 2
        }
    ]

    data = list(db.orders.find({"vendor_id": 0}, {
        "order_id": 1, "address": 1, "timestamp": 1,
        "order.qty": 1, "order.price": 1
    }))

    for record in data:
        order = record.pop('order')
        record['price'] = 0
        record['item_count'] = 0
        for item in order:
            record['price'] += item['price']
            record['item_count'] += item['qty']

    return basic_success(data)


def scan(request):
    return basic_success(20)
