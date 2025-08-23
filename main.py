import logging

from workers.info_collector import InfoCollector
from logging_config import setup_logging
from workers.merger import WBMedMerger
from workers.excel_formater import ExcelFormatter

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info(f'Запуск программы')
    info_collector = InfoCollector()
    merger = WBMedMerger()

    info = info_collector.collect_info()
    info_merged = merger.merge(info['wb_prices'], info['med_prices'], info['wb_stocks'])

    excel_formatter = ExcelFormatter(info_merged)
    excel_formatter.get_excel_for_comparison()


if __name__ == "__main__":
    main()
