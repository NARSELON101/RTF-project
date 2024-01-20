from django.shortcuts import render

import pandas as pd
import json
import datetime
import requests

TEMPLATE_VACANCY_HTML = """<div class="job">
            <h2 class="job-name">{0}</h2>
            <strong class="job-employer-name">Кампания: {1}</strong>

                <br>
                <strong class="job-salary">Зарплата: {2} {3}</strong>


                <br>
                <strong class="job-area-name">Название региона: {4}</strong>


                <br>
                <strong class="job-published-at">Дату публикации вакансии: {5}</strong>

</div>
"""


def get_vacancies_from_hh():
    curr_time = datetime.date.today()
    delta = datetime.timedelta(days=1)
    one_day_ago_time = curr_time - delta
    response = requests.get('https://api.hh.ru/vacancies/?text=(!"инженер программист") '
                            'OR (!"инженер разработчик") '
                            'OR (!"it инженер")&date_from={0}'.format(format(str(one_day_ago_time)))).text
    return json.loads(response)


def parse_hh_vacancies():
    vacancies = get_vacancies_from_hh()
    vacancies_df = pd.DataFrame(columns=['name', 'employer_name', 'salary',
                                         'salary_currency', 'area_name', 'published_at'])
    for vacancy in vacancies['items']:
        try:
            salary_from = vacancy.get('salary', 0).get('from', 0)
            if not salary_from:
                salary_from = 0

            salary_to = vacancy.get("salary", 0).get('to', 0)
            if not salary_to:
                salary_to = 0

            salary = abs(salary_to - salary_from)
            vacancies_df.loc[len(vacancies_df.index)] = [vacancy.get('name'),
                                                         vacancy.get("employer").get("name"),
                                                         salary,
                                                         vacancy.get('salary').get('currency'),
                                                         vacancy.get('area').get('name'),
                                                         vacancy.get('published_at')]
        except AttributeError:
            continue
    vacancies_df.to_csv('./parsed_vacancies_from_hh.csv', index=False)


def create_html_info_hh():
    df = pd.read_csv('./parsed_vacancies_from_hh.csv')
    df['published_at'] = df['published_at'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")).\
        apply(lambda x: x.strftime("%m.%d.%Y %H:%M"))
    html = ''
    for row in df.iterrows():
        for col in row:
            if not issubclass(type(col), int):
                tmp_str = TEMPLATE_VACANCY_HTML.format(*list(col.to_dict().values()))
                html += tmp_str

    with open('./main/templates/main/vacancies_from_hh.html', 'w', encoding='utf-8-sig') as file:
        file.write("""{% extends 'main/last_vacancies.html' %}\n{% load static %}\n{% block vacancies %}\n""")
        file.write(html)
        file.write("{% endblock %}")


def get_vacancies_from_hh_to_table():
    parse_hh_vacancies()
    create_html_info_hh()


def index(request):
    return render(request, 'main/index.html')


def about(request):
    return render(request, 'main/about.html')


def demand(request):
    return render(request, 'main/demand.html')


def geography(request):
    return render(request, 'main/geography.html')


def skills(request):
    return render(request, 'main/skills.html')


def last_vacancies(request):
    get_vacancies_from_hh_to_table()
    return render(request, 'main/vacancies_from_hh.html')
