from abc import ABC, abstractmethod
from io import BytesIO, StringIO

import pandas as pd

from DTO.dop_columns import DopColumnsDTO
from config import BASE_COLUMNS_NAME_WB, CLUB_PROCENT
from DTO.columns_dto import WBColumnsDTO


class RulesStrategy(ABC):
    def __init__(self):
        self.columns = WBColumnsDTO()
        self.dop_columns = DopColumnsDTO()

    @abstractmethod
    def apply_rule(self, data, **kwargs) -> pd.DataFrame:
        pass


class RuleOldCollectionsStrategy(RulesStrategy):
    def apply_rule(self, excel_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        articuls = [93956029, 93956898, 156089687, 93956903, 138866947, 156089784, 93957167, 93957231]
        excel_df_copy = excel_df[excel_df[self.columns.wb_article].isin(articuls)].copy()
        excel_df_copy[self.dop_columns.new_discount] = excel_df_copy[self.columns.equilibrium_discount]
        return excel_df_copy
