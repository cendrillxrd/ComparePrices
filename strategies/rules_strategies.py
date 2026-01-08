from abc import ABC, abstractmethod
from io import BytesIO, StringIO

import pandas as pd

from DTO.wb_dop_columns import WBDopColumnsDTO
from config import BASE_COLUMNS_NAME_WB, CLUB_PROCENT
from DTO.columns_dto import WBColumnsDTO


class RulesStrategy(ABC):
    def __init__(self):
        self.columns = WBColumnsDTO()
        self.dop_columns = WBDopColumnsDTO()

    @abstractmethod
    def apply_rule(self, data, **kwargs) -> pd.DataFrame:
        pass


class RuleThereIsMed(RulesStrategy):
    def apply_rule(self, excel_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        mask = excel_df[self.columns.med_price_with_discount] > 0

        # Обновляем max_discount_including_commission
        discount_col = self.dop_columns.max_discount_including_commission
        excel_df.loc[mask & (excel_df[discount_col] < 0), discount_col] = 50

        # Вычисляем new_discount
        excel_df.loc[mask, self.dop_columns.new_discount] = \
            excel_df.loc[mask, [self.columns.equilibrium_discount,
                                self.dop_columns.max_discount_including_commission]].min(axis=1)

        return excel_df


class RuleThereIsNOMed(RulesStrategy):
    def apply_rule(self, excel_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        mask_med = excel_df[self.columns.med_price_with_discount] == 0

        excel_df.loc[mask_med, self.dop_columns.max_discount_including_commission] = \
            excel_df.loc[mask_med, self.dop_columns.max_discount_including_commission].where(
                excel_df.loc[mask_med, self.dop_columns.max_discount_including_commission] >= 0,
                50
            )

        mask_purchase_minus_one = excel_df[self.columns.purchase] > 0
        mask_to_update_zero = mask_med & mask_purchase_minus_one
        excel_df.loc[mask_to_update_zero, self.dop_columns.new_discount] = 0

        mask_purchase_positive = excel_df[self.columns.purchase] == -1
        mask_base = mask_med & mask_purchase_positive

        mask_brand_ltb = excel_df[self.columns.brand] == 'LTB'

        # Создаем маску для года > 2022 в коллекции (с обработкой ошибок)
        try:
            # Извлекаем года из строки коллекции
            years_extracted = excel_df[self.columns.collection].str.findall(r'\d{4}')
            # Берем первый найденный год, конвертируем в число
            years_numeric = years_extracted.str[0].astype(float)
            # Создаем маску: год > 2022 и не NaN
            mask_year_gt_2022 = years_numeric <= 2022
        except:
            # Если не получается извлечь год, создаем маску из False
            mask_year_gt_2022 = pd.Series(False, index=excel_df.index)

        # Объединяем условия: LTB ИЛИ год > 2022
        mask_additional = mask_brand_ltb | mask_year_gt_2022

        # Финальная маска: med_price == 0 И purchase > 0 И (LTB ИЛИ год > 2022)
        mask_to_update_fifty = mask_base & mask_additional

        # 5. Устанавливаем new_discount = 50
        excel_df.loc[mask_to_update_fifty, self.dop_columns.new_discount] = 50

        return excel_df
