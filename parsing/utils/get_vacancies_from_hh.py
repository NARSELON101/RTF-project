import datetime

import requests
import json


def get_vacancies_from_hh():
    curr_time = datetime.date.today()
    delta = datetime.timedelta(days=1)
    one_day_ago_time = curr_time - delta
    response = requests.get('https://api.hh.ru/vacancies/?text=(!"инженер программист") '
                            'OR (!"инженер разработчик") '
                            'OR (!"it инженер")&date_from={0}'.format(format(str(one_day_ago_time)))).text

    with open("./parsed_info/vacancies_from_hh.json", 'w', encoding='utf_8_sig') as file:
        json.dump(json.loads(response), file, ensure_ascii=False, indent=4)
