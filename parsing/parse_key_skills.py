import threading
from collections import Counter
from parsing.utils.format_date import format_date
import pandas as pd
from matplotlib import pyplot as plt

KEY_SKILLS_BY_YEAR_AND_KEY = {}
KEY_SKILLS_BY_YEAR = {}


def fill_dicts_filtered_vacancies_key_skills(global_dict_key_skills, input_csv_file_name):
    vacancies = pd.read_csv(input_csv_file_name)
    tmp_dict = {}

    vacancies.key_skills = vacancies.copy().key_skills.astype(str)
    vacancies['published_at'] = vacancies['published_at'].apply(format_date).apply(int)
    vacancies.key_skills = vacancies.key_skills.apply(lambda skills: skills.split("\n"))

    for index, row in vacancies.iterrows():
        temp_counter = Counter(row.key_skills)
        if row.published_at in tmp_dict.keys():
            tmp_dict[row.published_at].update(temp_counter)
        else:
            tmp_dict.update({row.published_at: temp_counter})

    for counter in tmp_dict.values():
        counter.pop('nan')
    new_key_skills_dict = {}
    for key, value in tmp_dict.items():
        if value:
            new_key_skills_dict[key] = value.most_common(20)

    global_dict_key_skills.update(new_key_skills_dict)


def get_key_skills_info():
    # Запускаем в отдельных потоках, чтобы было быстрее
    processes = [threading.Thread(target=fill_dicts_filtered_vacancies_key_skills, args=(KEY_SKILLS_BY_YEAR_AND_KEY,
                                                                                         'filtered_vacancies.csv')),
                 threading.Thread(target=fill_dicts_filtered_vacancies_key_skills, args=(KEY_SKILLS_BY_YEAR,
                                                                                         'vacancies.csv'))
                 ]

    for process in processes:
        process.start()
    for process in processes:
        process.join()


get_key_skills_info()
print(KEY_SKILLS_BY_YEAR_AND_KEY)
print(KEY_SKILLS_BY_YEAR)

