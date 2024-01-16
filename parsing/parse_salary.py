import datetime
import math
import threading
import pandas as pd
import matplotlib.pyplot as plt

SALARY_DYNAMIC_BY_YEAR_DICT = {}
VACANCIES_COUNT_BY_YEAR_DICT = {}
SALARY_DYNAMIC_BY_YEAR_AND_KEY_DICT = {}
VACANCIES_COUNT_BY_YEAR_AND_KEY_DICT = {}
#
# LABELS_TO_PLOTS = {SALARY_DYNAMIC_BY_YEAR_DICT: "Динамика уровня зарплат по годам",
#                    VACANCIES_COUNT_BY_YEAR_DICT: "Динамика количества вакансий по годам",
#                    SALARY_DYNAMIC_BY_YEAR_AND_KEY_DICT: "Динамика уровня зарплат по годам для выбранной профессии",
#                    VACANCIES_COUNT_BY_YEAR_AND_KEY_DICT: "Динамика количества вакансий по годам для выбранной профессии"}

def format_date(text):
    date = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S%z")
    return date.strftime("%Y")


def fill_mean_salary(df_):
    df_['salary_to'] = df_['salary_to'].fillna(df_['salary_from'])
    df_['salary_from'] = df_['salary_from'].fillna(df_['salary_to'])

    df_["mean_salary"] = (df_.salary_to + df_.salary_from) / 2
    return df_


def salary_dynamic_by_year(df_, salary_dynamics_by_year):
    df_['published_at'] = df_['published_at'].apply(format_date).apply(int)
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
    df_['published_at'] = df_['published_at'].apply(format_date).apply(int)

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


def salary_by_city(df_, vacancy_name):
    valid_cities = df_[df_.name.str.contains(vacancy_name, case=False)]
    vacancies_count_by_city = valid_cities.groupby("area_name").size()

    vacancies_count = len(valid_cities)
    vacancies_count_by_city = vacancies_count_by_city[(vacancies_count_by_city / vacancies_count) > 0.01]

    valid_cities = valid_cities[valid_cities['area_name'].isin(vacancies_count_by_city.index)]
    valid_cities_mean_salaries = valid_cities.groupby("area_name")['mean_salary'].mean().apply(math.floor)

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

    print("Уровень зарплат по городам для выбранной профессии (в порядке убывания):", out_dict)
    return df_


def vacancies_percent_by_city(df_, vacancy_name):
    valid_cities = df_[df_.name.str.contains(vacancy_name, case=False)]
    vacancies_count_by_city = valid_cities.groupby("area_name").size()

    vacancies_count = len(valid_cities)
    vacancies_count_by_city = vacancies_count_by_city[(vacancies_count_by_city / vacancies_count) > 0.01]

    out_dict = (vacancies_count_by_city
                .apply(lambda x: x / vacancies_count).to_dict())

    out_dict = {key: round(value, 4) for key, value in out_dict.items()}
    out_dict = {key: value for key, value in sorted(out_dict.items(), key=lambda x: (x[1]), reverse=True)[0:10]}
    print("Доля вакансий по городам для выбранной профессии (в порядке убывания):", out_dict)


def fill_dicts_all_vacancies(salary_dynamics_by_year, vacancies_count_by_year_df):
    all_vacancies = pd.read_csv("vacancies.csv")
    (all_vacancies
     [(all_vacancies.salary_currency == "RUR")]
     .pipe(fill_mean_salary)
     .pipe(lambda x: salary_dynamic_by_year(x, salary_dynamics_by_year))
     .pipe(lambda x: vacancies_count_by_year(x, vacancies_count_by_year_df)))


def fill_dicts_filtered_vacancies(salary_dynamics, vacancies_count):
    filtered_vacancies = pd.read_csv("filtered_vacancies.csv")
    (filtered_vacancies
     [(filtered_vacancies.salary_currency == "RUR")]
     .pipe(fill_mean_salary)
     .pipe(lambda x: salary_dynamic_by_year_and_key(x, salary_dynamics))
     .pipe(lambda x: vacancies_count_by_year_and_key(x, vacancies_count)))


def build_barhs():
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
    plt.savefig('demand.png')


def get_demand_info():
    # Запускаем в отдельных потоках, чтобы было быстрее
    processes = [threading.Thread(target=fill_dicts_all_vacancies, args=(SALARY_DYNAMIC_BY_YEAR_DICT,
                                                                         VACANCIES_COUNT_BY_YEAR_DICT)),
                 threading.Thread(target=fill_dicts_filtered_vacancies, args=(SALARY_DYNAMIC_BY_YEAR_AND_KEY_DICT,
                                                                              VACANCIES_COUNT_BY_YEAR_AND_KEY_DICT))
                 ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    # Сохраняем графики
    build_barhs()


get_demand_info()
