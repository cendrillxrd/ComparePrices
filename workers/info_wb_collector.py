import logging

import pandas as pd

from DTO.columns_dto import WBColumnsDTO
from DTO.info_wb_dto import InfoWBDTO
from logging_config import setup_logging
from services.med import MEDService
from services.wb import WBService

setup_logging()
logger = logging.getLogger(__name__)


class InfoWBCollector:
    def __init__(self):
        self.wb = WBService()
        self.med = MEDService()
        self.wb_columns = WBColumnsDTO()

    def collect_info(self) -> InfoWBDTO:
        # wb_cards_prices = self.wb.get_wb_cards_prices()
        # wb_prices = self.wb.get_wb_prices()
        wb_prices = self.wb.get_wb_prices()

        # Берём список артикулов и парсим карточки по ним
        # nm_ids = wb_prices[self.wb_columns.wb_article].tolist()  # первая колонка = wb_article (nmID)
        # wb_cards_prices = self.wb.get_wb_cards_prices(nm_ids=nm_ids)
        # wb_cards_prices.to_excel('prices_wb.xlsx', index=False)

        med_prices = self.med.get_med_prices()
        med_collection_1 = self.med.get_med_collections_first(type='wb')
        med_collection_2 = self.med.get_med_collections_second(type='wb')
        med_collection_3 = self.med.get_med_collections_third(type='wb')
        med_collection_4 = self.med.get_med_collections_fourth(type='wb')
        wb_promotions = self.wb.get_wb_promotions_plan_discounts()
        wb_fbs_stocks = self.wb.get_wb_stocks('mp')
        wb_fbw_stocks = self.wb.get_wb_stocks('wb')

        articuls_fbs = wb_fbs_stocks[wb_fbs_stocks[self.wb_columns.stock_fbs] != 0][self.wb_columns.seller_article].unique()

        # 2. Находим уникальные артикулы из третьего датафрейма, где остаток FBS не равен нулю
        articuls_fbw = wb_fbw_stocks[wb_fbw_stocks[self.wb_columns.stock_fbw] != 0][self.wb_columns.seller_article].unique()

        # 3. Объединяем эти два списка артикулов в один (убираем дубликаты)
        articuls_to_keep = pd.concat([pd.Series(articuls_fbw), pd.Series(articuls_fbs)]).unique()

        wb_prices_needed = wb_prices.copy()
        # 4. Оставляем в первом датафрейме только те строки,
        #    где артикул продавца присутствует в полученном списке
        df1_filtered = wb_prices_needed[wb_prices_needed[self.wb_columns.seller_article].isin(articuls_to_keep)]
        nm_ids = df1_filtered[self.wb_columns.wb_article].tolist()  # первая колонка = wb_article (nmID)
        wb_cards_prices = self.wb.get_wb_cards_prices(nm_ids=nm_ids)
        wb_cards_prices.to_excel('prices_wb.xlsx', index=False)

        purchase = self.med.get_med_purchase()
        return InfoWBDTO(
            wb_cards_prices=wb_cards_prices,
            wb_prices=wb_prices,
            med_prices=med_prices,
            med_collection_1=med_collection_1,
            med_collection_2=med_collection_2,
            med_collection_3=med_collection_3,
            med_collection_4=med_collection_4,
            wb_promotions=wb_promotions,
            wb_fbs_stocks=wb_fbs_stocks,
            wb_fbw_stocks=wb_fbw_stocks,
            purchase=purchase
        )
