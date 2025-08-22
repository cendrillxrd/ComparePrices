import logging

from info_collector import InfoCollector
from config import FILE_PATH
from logging_config import setup_logging
from merge.merger import WBMedMerger

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info(f'Запуск программы')
    # info_collector = InfoCollector()
    # merger = WBMedMerger()
    #
    # info = info_collector.collect_info()
    # result = merger.merge(info['wb_prices'], info['med_prices'], info['wb_stocks'])
    # # df = wb_and_med_merge(wb, med)
    # result.to_csv('temp6.csv', index=False, encoding='cp1251')


if __name__ == "__main__":
    main()
