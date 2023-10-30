from bd.model import Shop,  Documents, Session
from arrow import utcnow, get
from pprint import pprint
from .util import  period_to_date, get_intervals, get_shops_in

import telebot
from typing import List, Tuple

name = "Приемка"
desc = "Собирает данные о приемке товара"
mime = 'text'


class ShopInput:
    desc = "Выберите магазин из списка"
    type = "SELECT"

    def get_options(self, session: Session):
        _in = ['20220501-11CA-40E0-8031-49EADC90D1C4',
               '20220501-DDCF-409A-8022-486441F27458',
               '20220501-9ADF-402C-8012-FB88547F6222',
               '20220501-3254-40E5-809E-AC6BB204D373',
               '20220501-CB2E-4020-808C-E3FD3CB1A1D4',
               '20220501-4D25-40AD-80DA-77FAE02A007E',
               '20220430-A472-40B8-8077-2EE96318B7E7',
               '20220506-AE5B-40BA-805B-D8DDBD408F24']
        output = []
        for item in get_shops_in(session, _in):
            # pprint(item["name"])
            output.append({
                "id": item["uuid"],
                "name": item["name"]
            })

        return output


class PeriodInput:
    name = "Магазин"
    desc = "Выберите период"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "day",
            'name': 'День'
        },
            {
                'id': "week",
                'name': 'Неделя'
            },
            {
                'id': "fortnight",
                'name': 'Две недели'
            },
            {
                'id': "month",
                'name': 'Месяц'
            }
        ]

        return output


class DayInput:
    desc = "Выберите дату"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['0']['period'])
        since = period_to_date(session['params']['inputs']['0']['period'])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        shop_id = session.params['inputs']['0']['shop']
        # pprint(intervals)

        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": shop_id,
                "x_type": "ACCEPT",
            }
        )
        _in = [doc['openDate'] for doc in documents]
        for left, right in intervals:
            pprint(left)
            if left[0:10] in _in:
                output.append({
                    "id": left,
                    "name": left[0:10]
                })

        return output


class OpenDateInput:
    desc = "Выберите дату начало пириода "
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session['params']['inputs']['0']['period'])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({
                "id": left,
                "name": left[0:10]
            })

        return output


class CloseDateInput:
    desc = "Выберите дату окончание пириода "
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = session['params']['inputs']['0']['openDate']
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)

        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({
                "id": left,
                "name": left[0:10]
            })

        return output


class DocumentsInput:
    desc = "Выберите дату"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        params = session.params['inputs']['0']
        since = get(params['openDate']).replace(hour=3, minute=00).isoformat()

        until = get(params['closeDate']).replace(hour=23, minute=00).isoformat()
        shop_id = params['shop']
        pprint([i.name for i in Shop.objects(uuid=shop_id)][0])

        documents = Documents.objects(__raw__={
            'closeDate': {'$gte': since, '$lt': until},
            'shop_id': shop_id,
            'x_type': 'ACCEPT',
        })
        # pprint(documents)
        for item in documents:
            output.append({
                "id": item['number'],
                "name": get(item['closeDate']).shift(hours=3).isoformat()[0:10]
            })
        return output


def get_inputs(session: Session):
    return {
        "shop": ShopInput,
        "period": PeriodInput,
        "openDate": OpenDateInput,
        'closeDate': CloseDateInput,
        'number': DocumentsInput
    }


def generate(session: Session):
    params = session.params['inputs']['0']

    shop_id = params['shop']
    number = params['number']
    documents = Documents.objects(__raw__={
        'number': int(number),
        'shop_id': shop_id,
        'x_type': 'ACCEPT',
    })
    pprint(documents)
    _dict = {}
    _sum = 0
    for element in documents:
        for trans in element['transactions']:
            if trans['x_type'] == 'REGISTER_POSITION':
                _sum += int(trans['sum'])
                _dict.update({trans['commodityName']: '{}п./{}/{}'.format(trans['quantity'], trans['resultPrice'],
                                                                          trans['sum'])})
    _dict.update({'sum': _sum})

    return [_dict]
