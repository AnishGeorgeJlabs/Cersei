from . import basic_success

def orders(request):
    orders_list=[{
        'name': 'Sumit',
        'phone': 8888888888,
        'address': '24/267, Agra Town, Chennai',
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
    {
        'name': 'Sumit',
        'phone': 8888888888,
        'address': '24/267, Agra Town, Chennai',
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
                'price': 50
            }
        ]
    },
    {
        'name': 'Sumit',
        'phone': 8888888888,
        'address': '24/267, Agra Town, Chennai',
        'order': [
            {
                'name': 'Chavanprash',
                'id': 5,
                'qty': 1,
                'price': 100
            },
            {
                'name': 'Red Label Tea',
                'id': 30,
                'qty': 1,
                'price': 150
            },
            {
                'name': 'Colgate',
                'id': 3,
                'qty': 1,
                'price': 50
            },
            {
                'name': 'Tata Tea',
                'id': 13,
                'qty': 1,
                'price': 120
            }
        ]
    }]

    return basic_success(orders_list)


def scan(request):
    return basic_success(20)


