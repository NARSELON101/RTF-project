import json
import math
import os.path

import pandas as pd
from parsing.utils.get_vacancies_from_hh import get_vacancies_from_hh


def parse_hh_vacancies():
    if not os.path.isfile("./parsed_info/vacancies_from_hh.json"):
        get_vacancies_from_hh()
        print("Парсим вакансии за последние 24 часа")

    f = open('./parsed_info/vacancies_from_hh.json', encoding='utf-8-sig')
    vacancies = json.load(f)

    vacancies_df = pd.DataFrame(columns=['name', 'employer_name', 'salary_from', 'salary_to', 'area_name'])
    for vacancy in vacancies['items']:
        try:
            vacancies_df.loc[len(vacancies_df.index)] = [vacancy.get('name'),
                                                         vacancy.get("employer").get("name"),
                                                         vacancy.get('salary').get('from', math.nan),
                                                         vacancy.get("salary").get('to', math.nan),
                                                         vacancy.get('area').get('name')]
        except AttributeError:
            continue

    vacancies_df.to_csv('./parsed_info/parsed_vacancies_from_hh.csv', index=False)