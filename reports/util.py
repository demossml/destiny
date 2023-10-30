from bd.model import Products, Documents, Session, Shop, Employees
# from tc.config import not_group, EVOTOR_TOKEN, EVOTOR_TOKEN_2, aks, employees, shop, sku_bonus_group, taba
from multiprocessing import Process, Queue
from arrow import utcnow, get
from collections import OrderedDict
import operator
from typing import List, Tuple


def format_message_list2(obj):
    text = ''
    messages = []
    if len(obj) > 0:
        for k, v in obj.items():
            key = str(k)
            val = str(v)
            total_len = (len(key) + len(val))
            pad = 31 - total_len % 31

            text += key

            if pad > 0:
                text += ' ' * pad

            if total_len > 31:
                text += ' ' * 2

            text += str(v)
            text += '\n'

        text += ''
        # parts = [your_string[i:i+n] for i in range(0, len(your_string), n)]
        index = 0
        size = 4000
        while len(text) > 0:
            part = text[index:index + size]
            index = part.rfind('\n')
            if index == -1:
                index = len(text)
            part = text[0:index]
            messages.append('```\n' + part + '\n```')
            text = text[index:].strip()
        return messages


def format_sell_groups(_dict):
    for k, v in _dict.items():
        # if v['col'] != 0:
        _dict[k] = '{}/{}'.format(v['col'], v['sum'])
    return _dict



# 1 оклад 800₽ const
# 2 набака за тт
# 3 надбавка по итогам учета
# 4 процент за аксы
# 5 250₽ за выполнение плана
# 6 ₽ за проданный мотивационный товар

# получает dict uuid товара по которому идет мотивация (k==uuid, v==int('₽')
def sku_bonus_(sku_bonus_group: dict, shops: dict, since: str, until: str):
    _dict = {}
    x_type = ['SELL']
    products_uuid = [k for k, v in sku_bonus_group.items()]
    for item in shops:
        # pprint(item["uuid"])
        # pprint(since)
        # pprint(until)
        # pprint(products_uuid)
        # products = Products.objects(
        #     shop_id__exact=item["uuid"], parentUuid__in=sku_bonus_group
        # ).only("uuid")
        # products_uuid = [element.uuid for element in products]
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": item["uuid"],
                'x_type': {'$in': x_type},
                "transactions.commodityUuid": {"$in": products_uuid},
            })
        sum_sell = 0
        if len(documents):
            # pprint(documents)
            for doc in documents:
                for trans in doc["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        sum_sell += sku_bonus_group[trans["commodityUuid"]]
        _dict[item["uuid"]] = sum_sell
    return _dict


# Получает список груп, процент от продаж, данные по магазинам(shops = Shop.objects() и период
# Отдает славарь (uuid  магазина: сумма премии сотрудника)
def bonus(group: list, percent: int, shops: dict, since: str, until: str):
    _dict = {}
    x_type = ['SELL']
    for item in shops:
        products = Products.objects(
            shop_id__exact=item["uuid"], parentUuid__in=group
        ).only("uuid")
        products_uuid = [element.uuid for element in products]
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": item["uuid"],
                'x_type': {'$in': x_type},
                "transactions.commodityUuid": {"$in": products_uuid},
            })
        sum_sell = 0
        for doc in documents:
            for trans in doc["transactions"]:
                if trans["x_type"] == "REGISTER_POSITION":
                    sum_sell += trans["sum"]

        _dict[item["uuid"]] = round(sum_sell / 100 * percent, 0)
    return _dict


# Получает период и данные по магазинам(shops = Shop.objects()
# Провиряет надбавки к зп
# Отдает словарь (uuid  магазина: сумма надбавки сотрудника)
def bonus_2(since: str, until: str, shops: dict):
    result_shop = {}
    result_employees = {}
    employees_ = {}
    for item in shops:
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": item["uuid"],
                "x_type": "SELL",

            }
        )
        shop_id = []
        index = 0
        # for doc in documents:
        #     for trans in doc["transactions"]:
        #         if index == 0:
        #             if trans["x_type"] == "DOCUMENT_OPEN":
        #                 if trans['userUuid'] in employees:
        #                     result_employees[item["uuid"]] = employees[trans['userUuid']]
        #                 if item["uuid"] in shop:
        #                     result_shop[item["uuid"]] = shop[item["uuid"]]
        #                     index += 1
        #             for i in Employees.objects(uuid__exact=trans['userUuid']):
        #                 if item["uuid"] not in employees_:
        #                     employees_[item["uuid"]] = i.uuid

    return result_employees, result_shop, employees_


# Получает период и данные по магазинам(shops = Shop.objects() процент прироста
# Сумма премии за выполнение плана, uuid группы и период
# Отдает славарь (uuid  магазина: сумма надбавки сотрудника)
def plan_sell(shops: dict, percent: int, bonus: int, since: str, until: str, group_id: str):
    # План продаж
    _dict = {}
    # Продажи за день
    _dict_2 = {}
    period = [7, 14, 21, 28]
    for shop in shops:
        for element in period:
            # pprint(shop['uuid'])
            since_2 = get(since).shift(days=-element).replace(hour=3, minute=00).isoformat()
            # pprint(since)
            until_2 = get(until).shift(days=-element).replace(hour=21, minute=00).isoformat()

            products = Products.objects(shop_id__exact=shop['uuid'], parentUuid__exact=group_id).only('uuid')
            products_uuid = [element.uuid for element in products]
            x_type = ['SELL', 'PAYBACK']
            documents = Documents.objects(__raw__={
                'closeDate': {'$gte': since_2, '$lt': until_2},
                'shop_id': shop['uuid'],
                'x_type': {'$in': x_type},
                'transactions.commodityUuid': {'$in': products_uuid}
            })

            sum_sell = 0

            for doc in documents:
                for trans in doc['transactions']:
                    if trans['x_type'] == 'REGISTER_POSITION':
                        if trans['commodityUuid'] in products_uuid:
                            # pprint(trans)
                            sum_sell += trans['resultSum']

            if shop['name'] in _dict:
                _dict[shop["uuid"]] += round((int(sum_sell) / 4 + int(sum_sell) / 4 / 100 * percent))
            else:
                _dict[shop["uuid"]] = round((int(sum_sell) / 4 + int(sum_sell) / 4 / 100 * percent))

            result = {}
            for k, v in _dict.items():
                if v < 1500:
                    result[k] = float(1500)
                else:
                    result[k] = v

            documents_2 = Documents.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': shop['uuid'],
                'x_type': {'$in': x_type},
                'transactions.commodityUuid': {'$in': products_uuid}
            })

            sum_sell_today = 0
            for doc_2 in documents_2:

                for trans in doc_2['transactions']:
                    if trans['x_type'] == 'REGISTER_POSITION':
                        if trans['commodityUuid'] in products_uuid:
                            # pprint(trans)
                            sum_sell_today += trans['resultSum']

            if shop["uuid"] in _dict_2:
                _dict_2[shop["uuid"]] += sum_sell_today
            else:
                _dict_2[shop["uuid"]] = sum_sell_today

        result_v = {}
        for k, v in result.items():
            for k_2, v_2 in _dict_2.items():
                if k == k_2:
                    if v == v_2:
                        result_v[k] = bonus
                    else:
                        result_v[k] = 0

    return result_v




def period_to_date(period: str) -> utcnow:
    if period == "day":
        return utcnow().replace(hour=3, minute=00).isoformat()
    if period == "week":
        return utcnow().shift(days=-7).replace(hour=3, minute=00).isoformat()
    if period == "fortnight":
        return utcnow().shift(days=-14).replace(hour=3, minute=00).isoformat()
    if period == "month":
        return utcnow().shift(months=-1).replace(hour=3, minute=00).isoformat()
    raise Exception("Period is not supported")


def get_intervals(
        min_date: str, max_date: str, unit: str, measure: float
) -> List[Tuple[str, str]]:
    output = []
    while min_date < max_date:
        # записывет в перменную temp минимальную дату плюс (unit: measure)
        temp = get(min_date).shift(**{unit: measure}).isoformat()
        # записывает в output пару дат min_date и  меньшую дату min_date max_date или temp
        output.append((min_date, min(temp, max_date)))
        # меняет значение min_date на temp
        min_date = temp
    return output


def format_message_list4(obj):
    # print(obj)
    text = ''
    messages = []
    if len(obj) > 0:
        for i in obj:
            for k, v in i.items():
                key = str(k)
                val = str(v)
                total_len = (len(key) + len(val))
                pad = 30 - total_len % 30

                text += key

                if pad > 0:
                    text += ' ' * pad

                if total_len > 30:
                    text += ' ' * 2

                text += str(v)
                text += '\n'
            text += '\n'
            text += '******************************'
            text += '\n'

        text += ''
        index = 0
        size = 4000
        while len(text) > 0:
            part = text[index:index + size]
            index = part.rfind('\n')
            if index == -1:
                index = len(text)
            part = text[0:index]
            messages.append('```\n' + part + '\n```')
            text = text[index:].strip()
        return messages


def category(session: Session, ):
    if session.params["inputs"]['x_type'] == 'CASH_INCOME':
        result = 'Внесение'
        return result
    if session.params["inputs"]['x_type'] == 'CASH_OUTCOME':
        result = 'Выплата'
        return 'Выплата'


def get_shops_in(session: Session, _in=[]):
    uuid = []
    # print(_in)
    users = [element.stores for element in Employees.objects(lastName=str(session.user_id))]
    # print(users)
    for i in users:
        for e in i:
            if e in _in:
                uuid.append(e)
            if session.user_id == 490899906:
                for el in _in:
                    uuid.append(el)
    return Shop.objects(uuid__in=uuid)
