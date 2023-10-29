from pprint import pprint

from bd.model import Session, Products

name = 'Редактировать группы'
desc = 'Редатировать группы добовляет удоляет группы товара'
mime = 'text'


class EditGroupsInput:
    name = "Выберите Удалить или Добавить группу"
    desc = "Выберите Удалить или Добавить группу"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "add",
            'name': 'Добавить группу'
        },
            {
                'id': "delete",
                'name': 'Удалить'
            },

        ]
        return output


class UuidGroupInput:
    name = "Выберите группу"
    desc = "Выберите для удаления группу"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []

        for item in Products.objects(group=True):
            output.append({
                'id': item['uuid'],
                'name': item['name']
            })
        return output


class NameInput:
    desc = "Напишите название группы "
    type = "MESSAGE"


# class DocStatusInput:
#     name = "Выберите продожить или закрыть документ"
#     desc = "Выберите продожить или закрыть документ"
#     type = 'SELECT'
#
#     def get_options(self, session: Session):
#         output = [{
#             'id': "open",
#             'name': 'Продожить'
#         },
#             {
#                 'id': "completed",
#                 'name': 'Закрыть документ'
#             },
#
#         ]
#         return output


def get_inputs(session: Session):
    room = session['room']
    if session.params["inputs"][room]:
        if session.params["inputs"][room]['edit'] == 'add':
            return {'name': NameInput,
                    # 'docStatus': DocStatusInput
                    }
        if session.params["inputs"][room]['edit'] == 'delete':
            return {
                'uuid': UuidGroupInput,
                # 'docStatus': DocStatusInput,
            }
        else:
            return {}
        # if session.params["inputs"][room]['docStatus'] == 'completed':
        #     return {}
    else:
        return {
            'edit': EditGroupsInput
        }


def generate(session: Session):
    params = session.params["inputs"]
    room = session['room']
    if params[room]['edit'] == 'add':
        if len(Products.objects(group=True)) > 0:
            uuid = [element['uuid'] for element in Products.objects(group=True).order_by("-uuid")]
        else:
            uuid = [0]
        prod = {
            'group': True,
            'uuid': str(int(uuid[0]) + 1),
            'brand': '0',
            'name': params[room]['name'],
            'photo': '0',
            'parentUuid': '0',
            'barCodes': '0',
            'costPrice': '0',
            'price': '0',
            'quantity': '0',
            'description': {
                'liquid_volume': 'null',
                'battery': 'null',
                'original': 'null',
                'charger': 'null',
                'resistance': 'null'
            },
            'tastes': '0'
        }
        # pprint(prod)
        Products.objects(group=True, uuid=prod['uuid']).update(**prod, upsert=True)

        return [{'Вы создали группу:': params[room]['name']}]
    if params[room]['edit'] == 'delete':
        name_ = [item['name'] for item in Products.objects(group=True, uuid=params[room]['uuid'])]
        Products.objects(group=True, uuid=params[room]['uuid']).delete()
        return [{'Вы удалили группу:': name_[0]}]
