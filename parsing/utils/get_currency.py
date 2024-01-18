import math

import pandas as pd
import io
from decimal import Decimal
import requests


def df_get_currency(currency_df):
    def _inner(row):
        if (isinstance(row["published_at"], float) or
                isinstance(row["salary_currency"], float) or
                row["salary_currency"] == "RUR"):
            return 1.0
        try:
            return currency_df.loc[row["published_at"].strftime("%Y/%m")].loc[row["salary_currency"]]
        except KeyError as e:
            return math.nan

    return _inner


def fetch_data_from_cb(url):
    def _inner(row):
        date: pd.Timestamp = row["date"]
        req = requests.get(f"{url}", {"date_req": date.strftime("%d/%m/%Y")})
        xml_text = io.StringIO(req.text)
        xml = pd.read_xml(xml_text, parser="etree",
                          converters={"Nominal": Decimal,
                                      "Value": lambda fstr: Decimal(fstr.replace(",", "."))})
        xml = xml[["CharCode", "Nominal", "Value"]]
        xml["Value"] = xml["Value"] / xml["Nominal"]
        xml["Value"] = xml["Value"].apply(float)
        res = xml["Value"]
        res.index = xml["CharCode"]
        res["date"] = date.strftime("%Y/%m")
        return res

    return _inner


def load_from_cb(file_name):
    columns = ["date", "BYR", "USD", "EUR", "KZT", "UAH", "AZN", "KGS", "UZS"]

    df = pd.DataFrame(columns=columns)
    df["date"] = pd.date_range("2003-01-1", "2023-01-01", freq="MS")
    df = df.apply(fetch_data_from_cb("https://www.cbr.ru/scripts/XML_daily.asp"), axis=1, result_type="expand")
    df = df[columns]
    df.to_csv(file_name, index=False)


if __name__ == "__main__":
    load_from_cb("../parsed_info/cb_currency.csv")
