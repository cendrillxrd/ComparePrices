from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import PatternFill
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter


class ExcelFormatter:
    def __init__(self, df):
        self.work_book = Workbook()
        self.df = df

    def get_excel_for_comparison(self):
        work_sheet = self.work_book.active

        work_sheet.delete_rows(1, work_sheet.max_row)

        yellow_fill = PatternFill(start_color='FFFF00',  # Желтый цвет
                                  end_color='FFFF00',
                                  fill_type='solid')
        green_fill = PatternFill(start_color='00FF00',
                                 end_color='00FF00',
                                 fill_type='solid')
        red_fill = PatternFill(start_color='FF0000',  # синий цвет
                               end_color='FF0000',
                               fill_type='solid')

        for row in dataframe_to_rows(self.df, index=False, header=True):
            work_sheet.append(row)

        work_sheet['G1'] = 'Скидка WB ●'
        work_sheet['H1'] = '(WB) Цена со скидкой WB ●'
        work_sheet['I1'] = 'Разность цен ●'

        for row in range(2, len(self.df) + 2):
            formula_wb_price = f'=PRODUCT(D{row},(1-G{row}/100))'
            formula_compare = f'=ABS(F{row}-H{row})'

            cell_price = work_sheet[f'H{row}']
            cell_price.value = formula_wb_price
            cell_price.fill = yellow_fill

            cell_compare = work_sheet[f'I{row}']
            cell_compare.value = formula_compare

            cell_discount = work_sheet[f'G{row}']
            cell_discount.fill = green_fill

        work_sheet.conditional_formatting.add(f'I2:I{len(self.df) + 2}',
                                              FormulaRule(formula=[f'ABS(F2-H2) >= 800'], stopIfTrue=True,
                                                          fill=red_fill))

        for col in work_sheet.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = max_length + 2
            work_sheet.column_dimensions[col_letter].width = adjusted_width

        self.work_book.save('compare_price.xlsx')
