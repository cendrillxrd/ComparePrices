# from med_client import MedClient
# from wildberries_api import WildberriesAPIClient
from merge.wb_med_merger import wb_and_med_merge
from client import WildberriesAPIClient, MedClient
from strategies.convert_strategies import *
from strategies.request_strategies import *
from converter import Converter

setup_logging()
logger = logging.getLogger(__name__)


class InfoCollector:
    def __init__(self):
        self.wb = WildberriesAPIClient()
        self.med = MedClient()

    def save_info(self):
        ...

    def get_wb_prices(self) -> pd.DataFrame:
        logger.info(f'Получение данных о ценах')
        prices_json = self.wb.get_data(ReqPricesStrategy())
        converter = Converter(PricesWBStrategy())
        prices_df = converter.convert(prices_json)
        return prices_df

    def get_med_prices(self) -> pd.DataFrame:
        # med_prices_csv = self.med.get_data()
        med_prices_csv = pd.read_csv('file_prices.csv')
        converter = Converter(PricesMEDStrategy())
        med_prices_df = converter.convert(med_prices_csv)
        return med_prices_df

    def get_info(self):
        wb_df = self.get_wb_prices()
        med_df = self.get_med_prices()
        wb_med_df = wb_and_med_merge(wb_df, med_df)
        return wb_med_df
