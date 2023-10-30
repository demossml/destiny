from arrow import utcnow, get
from bd.model import Session
from .util import  period_to_date, get_intervals
from pprint import pprint

name = 'Отчет по статье рас./прих. за период'
desc = 'Отчет по статье рас./прих. за период'
mime = 'text'


class X_typeInput:
    name = "Выберите отчет"
    desc = "Выберите отчет"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "CASH_INCOME",
            'name': 'Внесение'
        },
            {
                'id': "CASH_OUTCOME",
                'name': 'Выплаты'
            }]
        return output


class BaseCashOutcomeInput:
    desc = "Основание:"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [{
            "id": 'Аренда1',
            "name": 'Аренда1'
        },
            {
                "id": 'ЗП',
                "name": 'ЗП'
            },
            {
                "id": 'Аренда',
                "name": 'Аренда'
            },
            {
                "id": 'ГСМ',
                "name": 'ГСМ'
            },
            {
                "id": 'Мороженое',
                "name": 'Мороженое'
            },
            {
                "id": 'Закупка Товара',
                "name": 'Закупка Товара'
            },
            {
                "id": 'Прочие',
                "name": 'Прочие'
            },
        ]

        return output


class BaseCashIncomeInput:
    desc = "Основание:"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [{
            "id": 'Мороженое',
            "name": 'Мороженое'
        },
            {
                "id": 'Прочие',
                "name": 'Прочие'
            },

        ]

        return output


class PeriodOpenDateInput:
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


class OpenDateInput:
    desc = "Выберите дату начало пириода "
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session['params']['inputs']['periodOpenDate'])
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
        since = session['params']['inputs']['openDate']
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


def get_inputs(session: Session):
    params = session.params["inputs"]
    if 'x_type' in params:
        if params['x_type'] == 'CASH_INCOME':
            return {
                "base": BaseCashIncomeInput,
                "periodOpenDate": PeriodOpenDateInput,
                "openDate": OpenDateInput,
                'closeDate': CloseDateInput,
            }
        if params['x_type'] == 'CASH_OUTCOME':
            return {
                "base": BaseCashOutcomeInput,
                "periodOpenDate": PeriodOpenDateInput,
                "openDate": OpenDateInput,
                'closeDate': CloseDateInput,
            }

    else:
        return {"x_type": X_typeInput,

                }


def generate(session: Session):
    _dict = {}
    params = session.params["inputs"]

    since = get(params['openDate']).replace(hour=3, minute=00).isoformat()
    pprint(since)
    until = get(params['closeDate']).replace(hour=23, minute=00).isoformat()

    return [{1: 1}]
