import datetime
import math
import threading
import pandas as pd
import matplotlib.pyplot as plt
from utils.get_currency import df_get_currency
import pretty_html_table

SALARY_DYNAMIC_BY_YEAR_DICT = {}
VACANCIES_COUNT_BY_YEAR_DICT = {}
SALARY_DYNAMIC_BY_CITY = {}
VACANCIES_PERCENT_BY_CITY = {}

SALARY_DYNAMIC_BY_YEAR_AND_KEY_DICT = {}
VACANCIES_COUNT_BY_YEAR_AND_KEY_DICT = {}
SALARY_DYNAMIC_BY_CITY_AND_KEY = {}
VACANCIES_PERCENT_BY_CITY_AND_KEY = {}


def format_date(text):
    date = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S%z")
    return date.strftime("%Y")


def fill_mean_salary(df_):
    currency_df_ = pd.read_csv("./parsed_info/cb_currency.csv", index_col='date')

    df_['published_at'] = df_['published_at'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z"))

    df_["currency_val"] = df_.apply(df_get_currency(currency_df_), axis=1)
    df_['salary_to'] = df_['salary_to'].fillna(df_['salary_from'])
    df_['salary_from'] = df_['salary_from'].fillna(df_['salary_to'])

    df_["mean_salary"] = (df_.salary_to + df_.salary_from) / 2 * df_['currency_val']
    return df_


def salary_dynamic_by_year(df_, salary_dynamics_by_year):
    df_['published_at'] = df_['published_at'].apply(lambda x: x.strftime("%Y")).apply(int)
    salary_dynamics = (df_
                       .groupby('published_at')
                       ['mean_salary']
                       .mean()
                       .apply(math.floor)
                       .to_dict())

    salary_dynamics_by_year.update(salary_dynamics)

    return df_


def vacancies_count_by_year(df_, vacancies_count_by_year):
    vacancies_count_by_year_df = df_.groupby("published_at").size()
    vacancies_count_by_year_df = vacancies_count_by_year_df.to_dict()

    vacancies_count_by_year.update(vacancies_count_by_year_df)

    return df_


def salary_dynamic_by_year_and_key(df_, salary_dynamics_dict):
    df_['published_at'] = df_['published_at'].apply(lambda x: x.strftime("%Y")).apply(int)

    years_list = df_['published_at'].unique()
    salary_dynamics = (df_
                       .groupby('published_at')
                       ['mean_salary']
                       .mean()
                       .apply(math.floor)
                       .to_dict())

    for year in years_list:
        if year not in salary_dynamics.keys():
            salary_dynamics[year] = 0

    salary_dynamics = {key: value for key, value in sorted(salary_dynamics.items(), key=lambda x: x[0])}

    salary_dynamics_dict.update(salary_dynamics)

    return df_


def vacancies_count_by_year_and_key(df_, vacancies_count_by_year_and_k_dict):
    years_list = df_['published_at'].unique()

    vacancies_count_by_year_df = df_.groupby("published_at").size().to_dict()

    for year in years_list:
        if year not in vacancies_count_by_year_df.keys():
            vacancies_count_by_year_df[year] = 0

    vacancies_count_by_year_df = {key: value for key, value in
                                  sorted(vacancies_count_by_year_df.items(), key=lambda x: x[0])}

    vacancies_count_by_year_and_k_dict.update(vacancies_count_by_year_df)

    return df_


def salary_by_city(df_, salary_dynamic_by_city):
    vacancies_count_by_city = df_.groupby("area_name").size()

    vacancies_count = len(df_)
    vacancies_count_by_city = vacancies_count_by_city[(vacancies_count_by_city / vacancies_count) > 0.01]
    df_ = df_[df_['area_name'].isin(vacancies_count_by_city.index)]
    valid_cities_mean_salaries = df_.groupby("area_name")['mean_salary'].mean().apply(math.floor)

    sorted_dict = {key: value for key, value in sorted(valid_cities_mean_salaries.to_dict().items(),
                                                       key=lambda x: (x[1]),
                                                       reverse=True)}

    i = 1
    out_dict = {}
    for key, value in sorted_dict.items():
        if i > 10:
            break
        out_dict[key] = value
        i += 1

    salary_dynamic_by_city.update(out_dict)

    return df_


def vacancies_percent_by_city(df_, vacancies_percent_by_city_dict):
    vacancies_count_by_city = df_.groupby("area_name").size()

    vacancies_count = len(df_)
    vacancies_count_by_city = vacancies_count_by_city[(vacancies_count_by_city / vacancies_count) > 0.01]

    out_dict = (vacancies_count_by_city
                .apply(lambda x: x / vacancies_count))

    out_dict = {key: round(value, 4) for key, value in out_dict.items()}
    out_dict = {key: value for key, value in sorted(out_dict.items(), key=lambda x: (x[1]), reverse=True)[0:10]}

    vacancies_percent_by_city_dict.update(out_dict)


def fill_dicts_all_vacancies(salary_dynamics_by_year, vacancies_count_by_year_df,
                             salary_dynamic_by_city, vacancies_percent):
    all_vacancies = pd.read_csv("vacancies.csv", low_memory=False)
    (all_vacancies
     .pipe(fill_mean_salary)
     .pipe(lambda x: salary_dynamic_by_year(x, salary_dynamics_by_year))
     .pipe(lambda x: vacancies_count_by_year(x, vacancies_count_by_year_df))
     .pipe(lambda x: salary_by_city(x, salary_dynamic_by_city))
     .pipe(lambda x: vacancies_percent_by_city(x, vacancies_percent)))


def fill_dicts_filtered_vacancies(salary_dynamics, vacancies_count, salary_dynamic_by_city, vacancies_percent):
    filtered_vacancies = pd.read_csv("filtered_vacancies.csv", low_memory=False)
    (filtered_vacancies
     .pipe(fill_mean_salary)
     .pipe(lambda x: salary_dynamic_by_year_and_key(x, salary_dynamics))
     .pipe(lambda x: vacancies_count_by_year_and_key(x, vacancies_count))
     .pipe(lambda x: salary_by_city(x, salary_dynamic_by_city))
     .pipe(lambda x: vacancies_percent_by_city(x, vacancies_percent)))


def build_barhs_demand():
    fig, ax = plt.subplots(2, 2, figsize=(10, 8))
    df = pd.DataFrame(SALARY_DYNAMIC_BY_YEAR_DICT.items(), columns=['year', 'sec_value'])
    ax[0][0].barh(df['year'].apply(str), df['sec_value'])
    ax[0][0].set_title('Динамика уровня зарплат по годам', fontsize=12)

    df = pd.DataFrame(SALARY_DYNAMIC_BY_YEAR_AND_KEY_DICT.items(), columns=['year', 'sec_value'])
    ax[0][1].barh(df['year'].apply(str), df['sec_value'])
    ax[0][1].set_title('Динамика уровня зарплат по годам для выбранной профессии', fontsize=9)

    df = pd.DataFrame(VACANCIES_COUNT_BY_YEAR_DICT.items(), columns=['year', 'sec_value'])
    ax[1][0].barh(df['year'].apply(str), df['sec_value'])
    ax[1][0].set_title('Динамика количества вакансий по годам', fontsize=12)

    df = pd.DataFrame(VACANCIES_COUNT_BY_YEAR_AND_KEY_DICT.items(), columns=['year', 'sec_value'])
    ax[1][1].barh(df['year'].apply(str), df['sec_value'])
    ax[1][1].set_title('Динамика количества вакансий по годам для выбранной профессии', fontsize=8)

    plt.suptitle("Востребованность на рынке труда")
    plt.tight_layout()
    plt.savefig('../it_engeneer_vacancies/main/static/main/img/demand.png')


def create_html_table_file_from_dict(input_dict, file_name, columns_names):
    df = pd.DataFrame(list(input_dict.items()), columns=columns_names)
    with open(file_name, 'w', encoding='utf-8-sig') as file:
        file.write(pretty_html_table.build_table(df, 'grey_light'))


def build_barhs_geography():
    fig, ax = plt.subplots(2, 2, figsize=(10, 8))
    df = pd.DataFrame(SALARY_DYNAMIC_BY_CITY.items(), columns=['city', 'sec_value'])
    df.sort_values('sec_value', inplace=True)
    ax[0][0].barh(df['city'], df['sec_value'])
    ax[0][0].set_title('Уровень зарплат по городам', fontsize=12)

    df = pd.DataFrame(SALARY_DYNAMIC_BY_CITY_AND_KEY.items(), columns=['city', 'sec_value'])
    df.sort_values('sec_value', inplace=True)
    ax[0][1].barh(df['city'], df['sec_value'])
    ax[0][1].set_title('Уровень зарплат по городам для выбранной профессии', fontsize=9)

    df = pd.DataFrame(VACANCIES_PERCENT_BY_CITY.items(), columns=['city', 'sec_value'])
    df.sort_values('sec_value', inplace=True)
    ax[1][0].barh(df['city'], df['sec_value'])
    ax[1][0].set_title('Доля вакансий по городам', fontsize=12)

    df = pd.DataFrame(VACANCIES_PERCENT_BY_CITY_AND_KEY.items(), columns=['city', 'sec_value'])
    df.sort_values('sec_value', inplace=True)
    ax[1][1].barh(df['city'], df['sec_value'])
    ax[1][1].set_title('Доля вакансий по городам для выбранной профессии', fontsize=8)

    plt.suptitle("Востребованность в городах")
    plt.tight_layout()
    plt.savefig('../it_engeneer_vacancies/main/static/main/img/geography.png')


def get_demand_info():
    # Запускаем в отдельных потоках, чтобы было быстрее
    processes = [threading.Thread(target=fill_dicts_all_vacancies, args=(SALARY_DYNAMIC_BY_YEAR_DICT,
                                                                         VACANCIES_COUNT_BY_YEAR_DICT,
                                                                         SALARY_DYNAMIC_BY_CITY,
                                                                         VACANCIES_PERCENT_BY_CITY)),
                 threading.Thread(target=fill_dicts_filtered_vacancies, args=(SALARY_DYNAMIC_BY_YEAR_AND_KEY_DICT,
                                                                              VACANCIES_COUNT_BY_YEAR_AND_KEY_DICT,
                                                                              SALARY_DYNAMIC_BY_CITY_AND_KEY,
                                                                              VACANCIES_PERCENT_BY_CITY_AND_KEY))
                 ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()

    create_html_table_file_from_dict(SALARY_DYNAMIC_BY_YEAR_AND_KEY_DICT,
                                     '../it_engeneer_vacancies/main/templates/main/salary_dynamics_by_year_and_key.html',
                                     ['Год', 'Зарплата'])
    create_html_table_file_from_dict(VACANCIES_COUNT_BY_YEAR_AND_KEY_DICT,
                                     '../it_engeneer_vacancies/main/templates/main/vacancies_count_by_year_and_key.html',
                                     ['Год', 'Доля вакансий'])
    create_html_table_file_from_dict(SALARY_DYNAMIC_BY_CITY_AND_KEY,
                                     '../it_engeneer_vacancies/main/templates/main/salary_dynamics_by_city_and_key.html',
                                     ['Город', 'Зарплата'])
    create_html_table_file_from_dict(VACANCIES_PERCENT_BY_CITY_AND_KEY,
                                     '../it_engeneer_vacancies/main/templates/main/vacancies_percent_by_city_and_key.html',
                                     ['Город', 'Доля вакансий'])

    create_html_table_file_from_dict(SALARY_DYNAMIC_BY_YEAR_DICT,
                                     '../it_engeneer_vacancies/main/templates/main/salary_dynamics_by_year.html',
                                     ['Год', 'Зарплата'])
    create_html_table_file_from_dict(VACANCIES_COUNT_BY_YEAR_DICT,
                                     '../it_engeneer_vacancies/main/templates/main/vacancies_count_by_year.html',
                                     ['Год', 'Доля вакансий'])
    create_html_table_file_from_dict(SALARY_DYNAMIC_BY_CITY,
                                     '../it_engeneer_vacancies/main/templates/main/salary_dynamics_by_city.html',
                                     ['Город', 'Зарплата'])
    create_html_table_file_from_dict(VACANCIES_PERCENT_BY_CITY,
                                     '../it_engeneer_vacancies/main/templates/main/vacancies_percent_by_city.html',
                                     ['Город', 'Доля вакансий'])


    # Сохраняем графики
    build_barhs_demand()
    build_barhs_geography()


get_demand_info()
