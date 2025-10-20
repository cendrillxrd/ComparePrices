import logging

import pandas as pd

from config import EXCEL_FILE_NAME, TASKS_STATUS
from logging_config import setup_logging
from utils.bot_helper import send_notification_to_all, send_notification_to_admin
from utils.df_helper import get_seller_discount_df
from utils.excel_helper import load_excel_with_formulas
from workers.excel_formater import ExcelFormatter
from workers.info_collector import InfoCollector
from workers.info_redactor import InfoRedactor
from workers.price_updater import PriceUpdater
from DTO.columns_dto import ColumnsDTO

columns_dto = ColumnsDTO()
setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info(f'Запуск программы')
    info_collector = InfoCollector()
    info = info_collector.collect_info()

    info_redactor = InfoRedactor()
    info_redacted = info_redactor.redact_info(info)

    excel_formatter = ExcelFormatter(info_redacted)
    excel_formatter.get_excel_for_comparison()

    PRICE_UPDATE = False
    if PRICE_UPDATE:
        excel_df = load_excel_with_formulas(f'{EXCEL_FILE_NAME}.xlsx')
        price_updater = PriceUpdater()
        price_updater.update_prices(excel_df)

        df = pd.read_csv(f'{TASKS_STATUS}.csv')
        df_new_discounts_seller = pd.merge(df, get_seller_discount_df(excel_df), on=columns_dto.wb_article, how='left')
        csv_data = df_new_discounts_seller.to_csv(index=False)

        send_notification_to_admin(
            "Редактирование цен",
            "В файле можно посмотреть артикулы товаров и их статусы\n"
            "Статус 2 - Скидка изменена успешно\n"
            "Статус 3 - Скидку не удалось изменить, см. 'Текст ошибки'",
            csv_data=csv_data
        )

    # new_df = info_redacted[[
    #              'Артикул WB',
    #              '(WB) Скидка продавца',
    #              'Скидка WB',
    #              'РРЦ',
    #              'Остаток FBS',
    #              'Остаток FBW',
    #              'В пути к клиенту',
    #              'В пути от клиента',
    #              'Категория',
    #              '(MED) Цена со скидкой продавца',
    #              ]].copy()
    # new_df.to_csv('train_data.csv', mode='a', index=False, header=False, encoding='utf-8')

    # df_excel = pd.read_excel(f'{EXCEL_FILE_NAME}.xlsx')
    # new_df_excel = df_excel[['Артикул WB',
    #                          '(WB) Скидка продавца',
    #                          'Скидка WB',
    #                          'РРЦ',
    #                          'Остаток FBS',
    #                          'Остаток FBW',
    #                          'В пути к клиенту',
    #                          'В пути от клиента',
    #                          'Категория',
    #                          '(MED) Цена со скидкой продавца',
    #                          ]].copy()
    # new_df_excel['Максимальная скидка'] = 60
    # # test = new_df_excel.drop(['(WB) Скидка продавца', 'Скидка WB'], axis=1)
    #
    # new_df_excel.to_csv('compare_price_test.csv', index=False, encoding='utf-8')
    #
    # logger.info(f'Успешно завершено')


if __name__ == "__main__":
    main()
