import logging

from info_collector import InfoCollector
from config import FILE_PATH
from logging_config import setup_logging
from merge.merger import wb_and_med_merge

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info(f'Запуск программы')
    info_collector = InfoCollector()
    # wb = info_collector.get_wb_prices()
    # med = info_collector.get_med_prices()
    df = info_collector.get_wb_stocks()
    print(df)
    # df = wb_and_med_merge(wb, med)
    # df.to_csv('temp5.csv', index=False, encoding='cp1251')


if __name__ == "__main__":
    main()
