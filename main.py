import logging

from info_collector import InfoCollector
from config import FILE_PATH
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info(f'Запуск программы')
    info_collector = InfoCollector()
    info_collector.get_wb_prices()


if __name__ == "__main__":
    main()
