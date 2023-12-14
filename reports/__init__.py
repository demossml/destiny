# reports/__init__.py
from reports import (
    get_article_report,
    edit_groups,
    goods_posting,
    edit_product,
    product_sale,
    get_document,
    get_remains,
    get_accept,
    file_json_download,
    settings,
)


from bd.model import Session

user_id = [490899906, 1254862309]

id_1 = [1048044573, 831546483, 852360724]


def get_reports(session: Session):
    if session.user_id in user_id:
        return {
            # 'ice_cream_report': ice_cream_report,
            # 'cash_balance': cash_balance,
            # 'cash_flow': cash_flow,
            # 'get_article_report': get_article_report,
            "settings": settings,
            "edit_groups": edit_groups,
            "edit_product": edit_product,
            "goods_posting": goods_posting,
            "product_sale": product_sale,
            "get_document": get_document,
            "get_remains": get_remains,
            "file_json_download": file_json_download,
        }

    if session.user_id in id_1:
        return {
            # 'edit_groups': edit_groups,
            # 'edit_product': edit_product,
            # 'goods_posting': goods_posting,
            # 'product_sale': product_sale,
            "get_document": get_document,
            "get_remains": get_remains,
            # 'get_summ': get_summ
        }
    return {}


reports = {
    # 'cash_flow': cash_flow,
    "get_article_report": get_article_report,
    "edit_groups": edit_groups,
    "edit_product": edit_product,
    "goods_posting": goods_posting,
    "product_sale": product_sale,
    "get_document": get_document,
    "get_remains": get_remains,
    "get_acceptget_accept": get_accept,
    "file_json_download": file_json_download,
    "settings": settings,
}
