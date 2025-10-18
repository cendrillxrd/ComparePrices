import logging

import pandas as pd

from config import EXCEL_FILE_NAME
from logging_config import setup_logging
from utils.excel_helper import load_excel_with_formulas
from workers.excel_formater import ExcelFormatter
from workers.info_collector import InfoCollector
from workers.info_redactor import InfoRedactor
from workers.price_updater import PriceUpdater

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

    excel_df = load_excel_with_formulas(f'{EXCEL_FILE_NAME}.xlsx')
    PRICE_UPDATE = False
    if PRICE_UPDATE:
        price_updater = PriceUpdater(excel_df)
        price_updater.update_prices()


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
