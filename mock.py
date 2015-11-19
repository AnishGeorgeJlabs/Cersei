from . import basic_success
from . import basic_failure

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
                'qty': 1,
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
    if not details_map[order_id]:
        return basic_failure('Not found')
    else:
        return basic_success(details_map[order_id])

def orders(request):
    orders_list=[{
        'address':'24/267, Agra Town, Chennai',
        'price':130,
        'order_id':'order_1',
        '# of items':3
    },
    {
        'address':'24/267, China Town, Delhi',
        'price':100,
        'order_id':'order_2',
        '# of items':1
    },
    {
        'address':'23/267, Agra Palace, Mumbai',
        'price':110,
        'order_id':'order_3',
        '# of items':2
    }
    ]

    return basic_success(orders_list)


def scan(request):
    return basic_success(20)


