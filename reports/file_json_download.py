import json
from pprint import pprint
from bd.model import (
    Session,
    Products
)

name = "Загрузить данные"
desc = "Загружает данне из json в базу"
mime = "text"


class CollectionsInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "products", "name": "Products"},
         
        ]

        return output


class FileInput:
    name = "Файл"
    desc = "Отправте файл в формате json"
    type = "FILE"


def get_inputs(session: Session):
    return {"collection": CollectionsInput, "file": FileInput}


def add_collection(date_: str, collection: str):
    """Добавить данные из JSON-файла в указанную коллекцию MongoDB.

    Args:
        date_ (str): Путь к JSON-файлу, содержащему данные для добавления.
        collection (str): Название целевой коллекции MongoDB.

    Returns:
        None
    """
    # Словарь, который сопоставляет имена коллекций с соответствующими моделями
    collections = {     
        "products": Products,     
    }

    # Преобразуйте JSON-текст в Python-структуру данных (список словарей)
    data = json.loads(date_)
    # Итерируемся по данным из файла JSON
    for items in data:
        params = {}

        # Итерируемся по ключам и значениям в элементах данных
        for k, v in items.items():
            if k != "_id":
                params.update({k: v})
        # В зависимости от выбранной коллекции выполняем обновление данных
     
        if collection == "products":
            collections[collection].objects(uuid=params["uuid"]).update(
                **params, upsert=True
            )

   


def generate(session: Session):
    params = session.params["inputs"]["0"]
    collection = params["collection"]

    add_collection(params["file"], collection)

    return [{"Ok": " "}]
