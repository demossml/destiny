# Собирает данные о поступлении товара
# Создает документ и сохраняет его ва базу
# Изменяет остатки цену закупки и продажи в моент регистраци документа

from pprint import pprint
from arrow import utcnow, get

from bd.model import Session, Products, Documents

# название кнопки меню
name = 'Поступление товара'
desc = 'Поступление товара'
mime = 'text'


# собирает данные о формен оплаты и записывает их в бд
#  session.params["inputs"][str(i)]['payment']
class PaymentFormatInput:
    name = "Выберите форму оплаты"
    desc = "Выберите форму оплаты"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "cash",
            'name': 'Нал факт'
        },
            {
                'id': "duty",
                'name': 'Отсрочка платежа'
            },

        ]
        return output


#  выводит группы  и записывает выбранный группу в бд
#  session.params["inputs"][str(i)]['parentUuid']
class UuidGroupInput:
    name = "Выберите группу"
    desc = "Выберите группу"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []

        for item in Products.objects(group=True):
            # pprint(item['name'])
            output.append({
                'id': item['uuid'],
                'name': item['name']
            })
        return output


# выводит товара по рание вабраной группе  и записывает выбранный товар в бд
#  session.params["inputs"][str(i)]['uuid']


class UuidProductInput:
    name = "Выберите товар"
    desc = "Выберите товар"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # номер в session.params["inputs"]
        room = session['room']
        uuid = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(session['room']) + 1):
            # если в 'uuid' есть в session.params["inputs"][str(i)]
            if 'uuid' in session.params["inputs"][str(i)]:
                # если 'uuid' нет в словаре с ключем i в списке uuid
                if session.params["inputs"][str(i)]['uuid'] not in uuid:
                    # добовляет 'uuid' в список uuid
                    uuid.append(session.params["inputs"][str(i)]['uuid'])
        # Вытаскивает из бд session рание вабранны 'parentUuid' группы
        parentUuid = session.params["inputs"][room]['parentUuid']
        # проходит циклом по товару из бд рение вабранной группы parentUuid=parentUuid
        for item in Products.objects(group=False, parentUuid=parentUuid):
            # Если item['uuid'] нет в списке uuid
            if item['uuid'] not in uuid:
                # записывкет в output {'id': item['uuid'], 'name': item['name']}
                output.append({
                    'id': item['uuid'],
                    'name': '{}  ({}шт./{})'.format(item['name'], item['quantity'], item['price'])
                })
        return output


# зписвае данные о колличестве введеные пользоватилем
class QuantityInput:
    desc = "Напишите количество"
    type = "MESSAGE"


# зписвае данные о цене закупке введеные пользоватилем
class СostPrice:
    desc = "Напишите цену закупки за единицу продукта"
    type = "MESSAGE"


# зписвае данные о цене продажи введеные пользоватилем
class PriceInput:
    desc = "Напишите цену продажи за единицу продукта"
    type = "MESSAGE"


class DocStatusInput:
    name = "Выберите продожить или закрыть документ"
    desc = "Выберите продожить или закрыть документ"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "open",
            'name': 'Продожить'
        },
            {
                'id': "completed",
                'name': 'Закрыть документ'
            },

        ]
        return output


# выводит инпуты согласно условий
def get_inputs(session: Session):
    # номер в session.params["inputs"]
    room = session['room']
    # если session.params["inputs"][0] есть
    if session.params["inputs"]['0']:
        # если 'payment' есть в первом inputs
        if 'payment' in session.params["inputs"]['0']:
            # отдает список импутов
            return {
                'parentUuid': UuidGroupInput,
                'uuid': UuidProductInput,
                'quantity': QuantityInput,
                'costPrice': СostPrice,
                'price': PriceInput,
                'docStatus': DocStatusInput,
            }

    else:
        return {
            'payment': PaymentFormatInput
        }


def generate(session: Session):
    params = session.params["inputs"]
    doc = []
    sum_cost_price = 0
    payment = session.params["inputs"]['0']['payment']
    for i in range(int(session['room']) + 1):
        # pprint(params[str(i)]['uuid'])
        # вытаскиваеи продукт по 'uuid'
        product = Products.objects(__raw__={
            'uuid': int(params[str(i)]['uuid']),
            'group': False
        })
        # pprint(product)
        # проходит циклом по данным продукта
        for item in product:
            # pprint(item['name'])

            # записават в doc словарь с даннами о товаре
            doc.append({
                'group': False,
                'uuid': params[str(i)]['uuid'],
                'barCodes': item['barCodes'],
                'costPrice': params[str(i)]['costPrice'],
                'name': item['name'],
                'parentUuid': params[str(i)]['parentUuid'],
                'price': params[str(i)]['price'],
                'quantity': params[str(i)]['quantity'],
            })
        # pprint(doc)
        sum_cost_price += float(params[str(i)]['costPrice'])*float(params[str(i)]['quantity'])

    # сумма по закупке товара в doc

    if len(Documents.objects()) > 0:
        number = [element['number'] for element in Documents.objects().order_by("-number")]
    else:
        number = [0]
    document = {
        'closeDate': utcnow().isoformat(),
        'user_id': session.user_id,
        'number': str(int(number[0]) + 1),
        'transactions': doc,
        'payment': payment,
        'x_type': 'COMING'
    }
    # pprint(doc)
    # for item in doc['transactions']:
    #     # document['transactions']= item
    #     sum_cost_price += int(item['costPrice'])

    document.update(
        {'closeSum': sum_cost_price}
    )
    Documents.objects(closeDate=document['closeDate']).update(**document, upsert=True)
    result = [{'Дата': utcnow().isoformat()[0:10]}, {'Сумма': sum_cost_price}]
    # pprint(document)
    for item in document['transactions']:
        prod = Products.objects(__raw__={
            'uuid': int(item['uuid']),
            'group': False,
        })

        for i in prod:
            # pprint(int(i['quantity']))
            # pprint(int(item['quantity']))
            _dict = {'costPrice': item['costPrice'],
                     'price': item['price'],
                     'quantity': str(float(i['quantity']) + float(item['quantity']))
                     }
            # pprint(_dict)
            Products.objects(group=False, uuid=int(item['uuid'])).update(**_dict, upsert=True)
            result.append({
                'Наименование': i['name'],
                'Количество': item['quantity'],
                'Закупочная цена': '{}'.format(item['costPrice']),
                'Цена продажи': item['price']
            })
    # pprint(document)
    return result
