from arrow import utcnow, get
from bd.model import Session, Documents
from pprint import pprint
from .util import  period_to_date, get_intervals
import telebot
from typing import List, Tuple

name = 'Просмотр документов '
desc = "Просмотр документов по категории за период"
mime = 'text'


class X_typeInput:
    name = "Магазин"
    desc = "Выберите отчет"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "COMING",
            'name': 'Поступление'
        },
            {
                'id': "WRITE_OFF",
                'name': 'Списание'
            }]
        return output


class PeriodOpenDateInput:
    name = "Период"
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


class OpenDateInput:
    desc = "Выберите дату начало пириода "
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session['params']['inputs']['0']['periodOpenDate'])
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


class PeriodCloseDateInput:
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


class ComentInput:
    name = "Коментарий"
    desc = "Выберите коментарий"
    type = 'SELECT'

    def get_options(self, session: Session):
        params = session.params['inputs']['0']

        since = get(params['openDate']).replace(hour=3, minute=00).isoformat()

        until = get(params['closeDate']).replace(hour=23, minute=00).isoformat()

        x_type = params['x_type']

        documents = Documents.objects(__raw__={
            'closeDate': {'$gte': since, '$lt': until},
            'x_type': x_type,
        })
        output = []
        for doc in documents:
            output.append({
                'id': doc['comment'],
                'name': doc['comment']
            })

        return output


def get_inputs(session: Session):
    if session.params["inputs"]['0']:
        # если 'payment' есть в первом inputs
        if 'x_type' in session.params["inputs"]['0']:
            if session.params["inputs"]['0']['x_type'] == 'WRITE_OFF':
                return {
                    "periodOpenDate": PeriodOpenDateInput,
                    "openDate": OpenDateInput,
                    'closeDate': CloseDateInput,
                    'coment': ComentInput
                }
            if session.params["inputs"]['0']['x_type'] == 'COMING':
                return {
                    "periodOpenDate": PeriodOpenDateInput,
                    "openDate": OpenDateInput,
                    'closeDate': CloseDateInput,
                }
            else:
                return {}
    else:
        return{'x_type': X_typeInput}


def generate(session: Session):
    params = session.params['inputs']['0']

    since = get(params['openDate']).replace(hour=3, minute=00).isoformat()
    # pprint(since)
    until = get(params['closeDate']).replace(hour=23, minute=00).isoformat()
    # pprint(until)

    x_type = params['x_type']
    # pprint(x_type)

    if x_type == 'WRITE_OFF':
        coment = params['coment']
        # pprint(coment)
        documents = Documents.objects(__raw__={
            'closeDate': {'$gte': since, '$lt': until},
            'x_type': x_type,
            'comment': coment
        })
        # pprint(documents)
    else:
        pprint(2)
        coment = 'None'
        documents = Documents.objects(__raw__={
            'closeDate': {'$gte': since, '$lt': until},
            'x_type': x_type,
        })
    # pprint(documents)
    result = []
    for doc in documents:
        result.append({
            'Дата': doc['closeDate'][0:10],
            'comment': coment,
            '№': doc['number']
        })
        sum_ = 0
        for item in doc['transactions']:
            result.append({
                'Наименование:': item['name'],
                'Количество:': item['quantity'],
                'Закупочная цена:': '{}'.format(item['costPrice']),
                'Цена продажи:': item['price']
            })
            sum_ += float(item['costPrice'])*float(item['quantity'])
    result.append({
        'Итого сумма:': str(sum_),
    })
    return result
