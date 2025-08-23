import logging

from info_collector import InfoCollector
from config import FILE_PATH
from logging_config import setup_logging
from merge.merger import WBMedMerger
from excel_formater import ExcelFormatter

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info(f'Запуск программы')
    info_collector = InfoCollector()
    merger = WBMedMerger()

    info = info_collector.collect_info()
    result = merger.merge(info['wb_prices'], info['med_prices'], info['wb_stocks'])
    excel_formatter = ExcelFormatter(result)
    excel_formatter.get_excel_for_comparison()


if __name__ == "__main__":
    main()
