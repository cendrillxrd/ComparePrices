from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from utils.excel_helper import red_fill, yellow_fill, green_fill


COLUMNS = {
    "discount_wb": "Скидка WB ●",
    "wb_price_with_discount": "(WB) Цена со скидкой WB ●",
    "price_diff": "Разность цен ●",
    "med_price": "(MED) Цена со скидкой продавца",
    "wb_seller_price": "(WB) Цена со скидкой продавца",
}


class ExcelFormatter:
    def __init__(self, df):
        self.work_book = Workbook()
        self.df = df

    def get_excel_for_comparison(self):
        ws = self.work_book.active
        self._write_dataframe(ws)
        col_letters = self._map_columns()
        self._add_new_columns(ws, col_letters)
        self._fill_formulas(ws, col_letters)
        self._apply_conditional_formatting(ws, col_letters)
        self._auto_fit_columns(ws)
        self.work_book.save("compare_price.xlsx")

    def _write_dataframe(self, ws):
        for row in dataframe_to_rows(self.df, index=False, header=True):
            ws.append(row)

    def _map_columns(self):
        return {col: get_column_letter(i+1) for i, col in enumerate(self.df.columns)}

    def _add_new_columns(self, ws, col_letters):
        last_col_idx = len(self.df.columns)
        new_columns = [COLUMNS["discount_wb"], COLUMNS["wb_price_with_discount"], COLUMNS["price_diff"]]
        for i, col_name in enumerate(new_columns, start=1):
            col_letter = get_column_letter(last_col_idx + i)
            col_letters[col_name] = col_letter
            ws[f"{col_letter}1"] = col_name

    @staticmethod
    def _formula_wb_price(cols, row):
        return f"=PRODUCT({cols[COLUMNS['wb_seller_price']]}{row}, (1-{cols[COLUMNS['discount_wb']]}{row}/100))"

    @staticmethod
    def _formula_price_diff(cols, row):
        return f"=ABS({cols[COLUMNS['med_price']]}{row}-{cols[COLUMNS['wb_price_with_discount']]}{row})"

    def _fill_formulas(self, ws, cols):
        for row in range(2, len(self.df) + 2):
            cell_price = ws[f"{cols[COLUMNS['wb_price_with_discount']]}{row}"]
            cell_price.value = self._formula_wb_price(cols, row)
            cell_price.fill = yellow_fill

            cell_compare = ws[f"{cols[COLUMNS['price_diff']]}{row}"]
            cell_compare.value = self._formula_price_diff(cols, row)

            ws[f"{cols[COLUMNS['discount_wb']]}{row}"].fill = green_fill

    def _apply_conditional_formatting(self, ws, cols):
        last_row = len(self.df) + 2
        ws.conditional_formatting.add(
            f"{cols[COLUMNS['price_diff']]}2:{cols[COLUMNS['price_diff']]}{last_row}",
            FormulaRule(
                formula=[
                    f"ABS({cols[COLUMNS['med_price']]}2-{cols[COLUMNS['wb_price_with_discount']]}2) >= 800"
                ],
                stopIfTrue=True,
                fill=red_fill,
            ),
        )

    @staticmethod
    def _auto_fit_columns(ws):
        for col in ws.columns:
            max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2