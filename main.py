import logging

import pandas as pd

from workers.info_collector import InfoCollector
from workers.info_redactor import InfoRedactor
from logging_config import setup_logging
from workers.excel_formater import ExcelFormatter

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info(f'Запуск программы')
    # info_collector = InfoCollector()
    # info = info_collector.collect_info()
    #
    # info_redactor = InfoRedactor()
    # info_redacted = info_redactor.redact_info(info)
    info_redacted = pd.read_csv('info.csv', encoding='cp1251')
    excel_formatter = ExcelFormatter(info_redacted)
    excel_formatter.get_excel_for_comparison()
    logger.info(f'Успешно завершено')


if __name__ == "__main__":
    main()
