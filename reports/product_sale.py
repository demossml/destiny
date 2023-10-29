# Собирает данные о поступлении товара
# Создает документ и сохраняет его ва базу
# Изменяет остатки цену закупки и продажи в моент регистраци документа

from pprint import pprint
from arrow import utcnow, get

from bd.model import Session, Products, Documents

# название кнопки меню
name = 'Списание товара'
desc = 'Списание товара'
mime = 'text'


# собирает данные о формен оплаты и записывает их в бд
#  session.params["inputs"][str(i)]['payment']
class PriceFormatInput:
    name = 'Выберите цену списания'
    desc = 'Выберите цену списания'
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "costPrice",
            'name': 'По закупочной цене'
        },
            {
                'id': "price",
                'name': 'По розничной цене'
            },

        ]
        return output


class CommentInput:
    desc = "Напишите коментарий"
    type = "MESSAGE"


#  выводит группы  и записывает выбранный группу в бд
#  session.params["inputs"][str(i)]['parentUuid']
class UuidGroupInput:
    name = "Выберите группу"
    desc = "Выберите группу"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []

        for item in Products.objects(group=True):
            pprint(item['name'])
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
                    'name': '{}  ({}шт.)'.format(item['name'], item['quantity'])
                })
        return output


# зписвае данные о колличестве введеные пользоватилем
class QuantityInput:
    desc = "Напишите количество"
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
        if 'price' in session.params["inputs"]['0']:
            if 'comment' in session.params["inputs"]['0']:
                # отдает список импутов
                return {
                    'parentUuid': UuidGroupInput,
                    'uuid': UuidProductInput,
                    'quantity': QuantityInput,
                    'docStatus': DocStatusInput,
                }
            else:
                return{'comment': CommentInput}
    else:
        return {
            'price': PriceFormatInput,

        }


def generate(session: Session):
    params = session.params["inputs"]
    doc = []
    price = session.params["inputs"]['0']['price']
    comment = session.params["inputs"]['0']['comment']
    for i in range(int(session['room']) + 1):
        # вытаскиваеи продукт по 'uuid'
        product = Products.objects(__raw__={
            'uuid': int(params[str(i)]['uuid']),
            'group': False,
        })
        # проходит циклом по данным продукта
        for item in product:

            doc.append({
                'group': False,
                'uuid': item['uuid'],
                'barCodes': item['barCodes'],
                'costPrice': item['costPrice'],
                'name': item['name'],
                'parentUuid': item['parentUuid'],
                'price': item['price'],
                'quantity': params[str(i)]['quantity'],
            })
    # сумма по закупке товара в doc
    sum_cost_price = 0
    sum_price = 0

    if len(Documents.objects()) > 0:
        number = [element['number'] for element in Documents.objects().order_by("-number")]
    else:
        number = [0]
    document = {
        'closeDate': utcnow().isoformat(),
        'user_id': session.user_id,
        'number': str(int(number[0]) + 1),
        'transactions': doc,
        'comment': comment,
        'price': price,
        'x_type': 'WRITE_OFF'
    }
    # pprint(doc)
    for item in doc:
        # document['transactions']= item
        sum_cost_price += float(item['costPrice'])
        sum_price += float(item['price'])
    if params['0']['price'] == 'price':
        pr = 'Сумма по розничной цене'
        _sum = sum_price
        document.update(
            {'closeSum': sum_price})
    else:
        pr = 'Сумма по закупочной цене'
        _sum = sum_cost_price
        document.update(
            {'closeSum': sum_cost_price}
        )
        Documents.objects(closeDate=document['closeDate']).update(**document, upsert=True)

    result = [{'Дата': utcnow().isoformat()[0:10]},
              {pr: _sum},
              {'Коментарий:': comment},
              {'№': str(int(number[0]) + 1)}
              ]

    for item in document['transactions']:
        prod = Products.objects(__raw__={
            'uuid': int(item['uuid']),
            'group': False,
        })

        for i in prod:
            # pprint(int(i['quantity']))
            # pprint(int(item['quantity']))
            _dict = {
                'quantity': str(float(i['quantity']) - float(item['quantity']))
            }
            Products.objects(group=False, uuid=item['uuid']).update(**_dict, upsert=True)
            result.append({

                'Наименование': i['name'],
                'Количество': item['quantity'],
                'Закупочная цена': '{}'.format(item['costPrice']),
                'Цена продажи': item['price']
            })
    # pprint(document)
    return result
