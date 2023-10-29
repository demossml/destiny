from pprint import pprint

from bd.model import Session, Products

name = 'Редактировать продукт'
desc = 'Редатировать продукты добовляет/удоляет  товар'
mime = 'text'


class EditGroupsInput:
    name = "Выберите Удалить или Добавить продукт"
    desc = "Выберите Удалить или Добавить продукт"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "add",
            'name': 'Добавить продукт'
        },
            {
                'id': "delete",
                'name': 'Удалить  продукт'
            },

        ]
        return output


class ParentUuidInput:
    name = "Выберите группу"
    desc = "Выберите"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []

        for item in Products.objects(group=True):
            output.append({
                'id': item['uuid'],
                'name': item['name']
            })
        return output


class UuidGroupInput:
    name = "Выберите группу"
    desc = "Выберите"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []

        for item in Products.objects(group=True):
            output.append({
                'id': item['uuid'],
                'name': item['name']
            })
        return output


class UuidProductInput:
    name = "Выберите товар"
    desc = "Выберите товар"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        room = session['room']
        parentUuid = session.params["inputs"][room]['parentUuid']
        for item in Products.objects(group=False, parentUuid=parentUuid):
            output.append({
                'id': item['uuid'],
                'name': '{}  ({}шт.)'.format(item['name'], item['quantity'])
            })
        return output


class NameInput:
    desc = "Напишите название"
    type = "MESSAGE"


class BarCodesInput:
    desc = "Напишите штрихкода через запятую или слово нет "
    type = "MESSAGE"


def get_inputs(session: Session):
    room = session['room']
    if session.params["inputs"][room]:
        if session.params["inputs"][room]['edit'] == 'add':
            return {
                'parentUuid': ParentUuidInput,
                'name': NameInput,
                'barCodes': BarCodesInput,
            }
        if session.params["inputs"][room]['edit'] == 'delete':
            return {
                'parentUuid': UuidGroupInput,
                'uuid': UuidProductInput,

                    }
        else:
            return {}
    else:
        return {
            'edit': EditGroupsInput
        }


def generate(session: Session):
    params = session.params["inputs"]
    room = session['room']
    if params[room]['edit'] == 'add':
        if len(Products.objects(group=False)) > 0:
            uuid = [element['uuid'] for element in Products.objects(group__exact=False).order_by("-uuid")]
            pprint(uuid)
        else:
            uuid = [0]
        prod = {
            'group': False,
            'uuid': int(uuid[0]) + 1,
            'name': params[room]['name'],
            'parentUuid': params[room]['parentUuid'],
            'barCodes': params[room]['barCodes'],
            'costPrice': '0',
            'price': '0',
            'quantity': '0',

        }
        pprint(prod)
        Products.objects(group=False, uuid=prod['uuid']).update(**prod, upsert=True)

        return [{'Вы создали продукт:': params[room]['name']}]
    if params[room]['edit'] == 'delete':
        name_ = [item['name'] for item in Products.objects(group=False, uuid=params[room]['uuid'])]
        Products.objects(group=False, uuid=params[room]['uuid']).delete()
        return [{'Вы удалили': name_[0]}]
