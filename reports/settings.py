from bd.model import Session, Documents, Products

name = "🛠 Настройки ➡️".upper()
desc = ""
mime = "text"


class ReportsSettingsInput:
    """
    Меню настроек бота
    """

    name = "Выберете".upper()
    desc = "Выберете".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "clear_db", "name": "Очистить базу данных ➡️".upper()},
        ]
        return output


class ReportsClearDbInput:
    """
    Меню очистки базы данных
    """

    name = "Выберете".upper()
    desc = "Выберете".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "clear_db_documents", "name": "📑 Очистить (Документы) ➡️".upper()},
            {"id": "clear_db_products", "name": "🛒 Очистить (Продукты) ➡️".upper()},
        ]
        return output


def get_inputs(session: Session):
    # Если входные параметры сессии существуют
    if session.params["inputs"]["0"]:
        # Если тип отчета - "shift_opening_report"
        if session.params["inputs"]["0"]["report"] == "clear_db":
            return {"clear": ReportsClearDbInput}

    else:
        return {
            "report": ReportsSettingsInput,
        }


def generate(session: Session):
    params = {}
    collection = {
        "clear_db_documents": Documents,
        "clear_db_products": Products,
    }
    clear_collection_name = session.params["inputs"]["0"]["clear"]

    clear_collection = collection[clear_collection_name]

    clear_collection.drop_collection()

    return [{"Коллекция": "Очищена"}]
