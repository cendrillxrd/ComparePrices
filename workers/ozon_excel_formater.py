import logging

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.datavalidation import DataValidation

from DTO.ozon_columns_dto import OZONColumnsDTO
from DTO.ozon_dop_columns import OZONDopColumnsDTO
from config import BASE_MP_COMMISSION, WB_EXCEL_FILE_NAME, OZON_EXCEL_FILE_NAME
from logging_config import setup_logging
from utils.excel_helper import (blue_fill, green_fill, orange_fill, pink_fill,
                                red_fill, yellow_fill, ozon_color_fill, light_green_fill)
from DTO.wb_dop_columns import WBDopColumnsDTO, asdict
from DTO.columns_dto import WBColumnsDTO

setup_logging()
logger = logging.getLogger(__name__)


class OZONExcelFormatter:
    def __init__(self, df):
        self.work_book = Workbook()
        self.df = df
        self.main_columns_dto = OZONColumnsDTO()
        self.new_columns_dto = OZONDopColumnsDTO()
        self.actual_columns = []
        self._create_percentage_style()

    def get_excel_for_comparison(self):
        logger.info('Генерация excel файла')
        ws = self.work_book.active
        ws.title = "Сравнение цен"

        self._add_new_columns_to_dataframe()

        self._write_dataframe(ws)
        col_letters = self._map_columns()
        self._make_headers_bold(ws)
        self._fill_formulas(ws, col_letters)
        self._add_dropdown_list(ws, col_letters)
        self._apply_percentage_format(ws, col_letters)
        self._apply_conditional_formatting(ws, col_letters)
        self._auto_fit_columns(ws)
        self.work_book.save(f"{OZON_EXCEL_FILE_NAME}.xlsx")

    def _add_new_columns_to_dataframe(self):
        """Добавляет новые колонки в датафрейм"""
        new_columns = asdict(self.new_columns_dto)
        for col_name in new_columns.values():
            if col_name not in self.df.columns:
                self.df[col_name] = ""  # Добавляем пустые колонки

    def _write_dataframe(self, ws):
        # Переупорядочиваем колонки, чтобы выпадающий список был между РРЦ и Остаток FBS
        for col in self.df.columns:
            if col not in (self.new_columns_dto.solution, self.new_columns_dto.new_price):
                if col == self.main_columns_dto.price_without_discount:  # Перед РРЦ
                    # Добавляем колонку с выпадающим списком
                    self.actual_columns.append(self.new_columns_dto.solution)
                self.actual_columns.append(col)
                if col == self.main_columns_dto.seller_discount:  # После скидки продавца
                    # Добавляем колонку с новой ценой
                    self.actual_columns.append(self.new_columns_dto.new_price)

        # Переупорядочиваем датафрейм
        ordered_df = self.df.reindex(columns=self.actual_columns)

        for row in dataframe_to_rows(ordered_df, index=False, header=True):
            ws.append(row)

    def _map_columns(self) -> dict:
        return {col: get_column_letter(i + 1) for i, col in enumerate(self.actual_columns)}

    @staticmethod
    def _make_headers_bold(ws):
        """Делает заголовки столбцов жирными"""
        bold_font = Font(bold=True)
        for cell in ws[1]:  # Первая строка содержит заголовки
            cell.font = bold_font

    def _create_percentage_style(self):
        """Создает стиль для процентного формата с целой частью"""
        percentage_style = NamedStyle(name="percentage_integer_style")
        percentage_style.number_format = '0%'  # Только целая часть процента
        if "percentage_integer_style" not in self.work_book.named_styles:
            self.work_book.add_named_style(percentage_style)

    def _apply_percentage_format(self, ws, cols):
        """Применяет процентный формат только с целой частью к определенным столбцам"""
        # Определяем колонки, которые должны быть в процентном формате
        percentage_columns = [
            self.new_columns_dto.mp_commission,
            self.new_columns_dto.mu_original,
            self.new_columns_dto.mu_with_our_discount,
            self.new_columns_dto.mu_with_discount_from_the_price_with_spp,
            self.new_columns_dto.mu_taking_into_account_the_wb_commission,
            self.new_columns_dto.max_discount_including_commission
        ]

        for col_name in percentage_columns:
            if col_name in cols:
                col_letter = cols[col_name]
                # Применяем формат ко всем ячейкам в колонке (начиная со 2-й строки)
                for row in range(2, len(self.df) + 2):
                    cell = ws[f"{col_letter}{row}"]
                    cell.style = "percentage_integer_style"

    def _formula_mu_original(self, columns, row):
        formula = f"={columns[self.main_columns_dto.price_without_discount]}{row} / {columns[self.main_columns_dto.purchase]}{row} - 1"
        return formula

    def _formula_mu_with_our_discount(self, columns, row):
        formula = f"={columns[self.main_columns_dto.price_with_seller_discount]}{row} / {columns[self.main_columns_dto.purchase]}{row} - 1"
        return formula

    def _formula_mu_with_discount_from_the_price_with_spp(self, columns, row):
        formula = f"={columns[self.main_columns_dto.price_with_ozon_club]}{row} / {columns[self.main_columns_dto.purchase]}{row} - 1"
        return formula

    def _formula_mu_taking_into_account_the_wb_commission(self, columns, row):
        formula = (f"=({columns[self.main_columns_dto.price_with_seller_discount]}{row} - {columns[self.main_columns_dto.price_with_seller_discount]}{row} *"
                   f" {columns[self.new_columns_dto.mp_commission]}{row}) / {columns[self.main_columns_dto.purchase]}{row} - 1")
        return formula

    def _formula_max_discount_including_commission(self, columns, row):
        formula = f"=1 - {columns[self.main_columns_dto.purchase]}{row} / (1 - {columns[self.new_columns_dto.mp_commission]}{row}) / {columns[self.main_columns_dto.price_without_discount]}{row}"
        return formula

    def _fill_formulas(self, ws, cols):
        for row in range(2, len(self.df) + 2):
            ws[f"{cols[self.new_columns_dto.mp_commission]}{row}"] = BASE_MP_COMMISSION
            ws[f"{cols[self.new_columns_dto.mu_original]}{row}"] = self._formula_mu_original(cols, row)
            ws[f"{cols[self.new_columns_dto.mu_with_our_discount]}{row}"] = self._formula_mu_with_our_discount(cols,row)
            ws[f"{cols[self.new_columns_dto.mu_with_discount_from_the_price_with_spp]}{row}"] = self._formula_mu_with_discount_from_the_price_with_spp(cols, row)
            ws[f"{cols[self.new_columns_dto.mu_taking_into_account_the_wb_commission]}{row}"] = self._formula_mu_taking_into_account_the_wb_commission(cols, row)
            ws[f"{cols[self.new_columns_dto.max_discount_including_commission]}{row}"] = self._formula_max_discount_including_commission(cols, row)

            ws[f"{cols[self.main_columns_dto.ozon_discount]}{row}"].fill = ozon_color_fill
            ws[f"{cols[self.main_columns_dto.seller_discount]}{row}"].fill = green_fill
            ws[f"{cols[self.new_columns_dto.new_price]}{row}"].fill = yellow_fill
            ws[f"{cols[self.main_columns_dto.equilibrium_price]}{row}"].fill = light_green_fill

            columns_for_blue = [self.main_columns_dto.price_with_ozon_discount,
                                self.main_columns_dto.med_price_with_discount,]
            for col_name in columns_for_blue:
                ws[f"{cols[col_name]}{row}"].fill = blue_fill

    def _add_dropdown_list(self, ws, cols):
        """Добавляет выпадающий список в указанную колонку"""
        if self.new_columns_dto.solution not in cols:
            return

        dropdown_col = cols[self.new_columns_dto.solution]

        # Создаем валидацию данных для выпадающего списка
        dv = DataValidation(
            type="list",
            formula1='"переоценка по МЕД,подсортировка,оставляем и продвигаем,возвращаем на склад,продаем с доп скидкой ВБ,увеличиваем скидку,нет остатка обнулить скидку"',
            allow_blank=True,
            showErrorMessage=True
        )

        # Применяем к колонке (со 2-й строки до конца данных)
        dv.add(f"{dropdown_col}2:{dropdown_col}{len(self.df) + 1}")
        ws.add_data_validation(dv)

    def _apply_conditional_formatting(self, ws, cols):
        last_row = len(self.df) + 2
        price_range = f"{cols[self.main_columns_dto.price_difference]}2:" \
                      f"{cols[self.main_columns_dto.price_difference]}{last_row}"
        rule_red = FormulaRule(
            formula=[f"{cols[self.main_columns_dto.med_price_with_discount]}2 - "
                     f"{cols[self.main_columns_dto.price_with_ozon_discount]}2 >= 1000"],
            stopIfTrue=True,
            fill=red_fill
        )

        rule_orange = FormulaRule(
            formula=[f"{cols[self.main_columns_dto.price_with_ozon_discount]}2 - "
                     f"{cols[self.main_columns_dto.med_price_with_discount]}2 >= 1000"],
            stopIfTrue=True,
            fill=orange_fill
        )

        ws.conditional_formatting.add(price_range, rule_red)
        ws.conditional_formatting.add(price_range, rule_orange)

    @staticmethod
    def _auto_fit_columns(ws):
        for col in ws.columns:
            max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2
