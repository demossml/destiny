# Собирает данные о поступлении товара
# Создает документ и сохраняет его ва базу
# Изменяет остатки цену закупки и продажи в моент регистраци документа

from pprint import pprint

from bd.model import Session, Products

# название кнопки меню
name = 'Остатки товара'
desc = 'Остатки товара'
mime = 'text'


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


# выводит инпуты согласно условий
def get_inputs(session: Session):
    return {
        'parentUuid': UuidGroupInput,

    }


def generate(session: Session):
    params = session.params["inputs"]['0']
    result = []
    price = []
    comment = []

    prod = Products.objects(__raw__={
        'parentUuid': params['parentUuid'],
        'group': False,
        })
    _dict = {}
    sum_ = 0
    for i in prod:
        # pprint(int(i['quantity']))
        # pprint(int(item['quantity']))
        sum_ += float(i['quantity'])*float(i['costPrice'])
        _dict.update({i['name']: i['quantity']})
    _dict.update({'итого': sum_})
    # pprint(document)
    return [_dict]
