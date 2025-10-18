from openpyxl.styles import PatternFill
import xlwings as xw
import pandas as pd
from DTO.columns_dto import ColumnsDTO
from DTO.dop_columns import DopColumnsDTO

columns_dto = ColumnsDTO()
dop_columns_dto = DopColumnsDTO()

yellow_fill = PatternFill(start_color='FFFF00',  # Желтый цвет
                          end_color='FFFF00',
                          fill_type='solid')
green_fill = PatternFill(start_color='c9eaa9',  # Зеленый цвет
                         end_color='c9eaa9',
                         fill_type='solid')
red_fill = PatternFill(start_color='FF0000',  # Красный цвет
                       end_color='FF0000',
                       fill_type='solid')
orange_fill = PatternFill(start_color="FFA500",
                          end_color="FFA500",
                          fill_type="solid")
blue_fill = PatternFill(start_color="9FD6E5",
                          end_color="9FD6E5",
                          fill_type="solid")

pink_fill = PatternFill(start_color="EC6FD8",
                        end_color="EC6FD8",
                        fill_type="solid")


def load_excel_with_formulas(filename: str) -> pd.DataFrame:
    app = xw.App(visible=False)  # Excel в фоне
    wb = app.books.open(filename)

    # Принудительно пересчитать все формулы
    wb.app.calculate()

    ws = wb.sheets[0]  # Первый лист
    df = ws.used_range.options(pd.DataFrame, header=1, index=False).value

    wb.close()
    app.quit()

    percent_columns = [dop_columns_dto.mp_commission,
                       dop_columns_dto.mu_original,
                       dop_columns_dto.mu_with_our_discount,
                       dop_columns_dto.mu_with_discount_from_the_price_with_spp,
                       dop_columns_dto.mu_taking_into_account_the_wb_commission,
                       dop_columns_dto.max_discount_including_commission]
    for col in percent_columns:
        if col in df.columns:
            df[col] = (df[col] * 100).round().astype(int)

    return df
