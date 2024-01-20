import pandas as pd
import pretty_html_table
from parsing.parsed_info.parsed_key_skills import KEY_SKILLS_BY_YEAR_AND_KEY, KEY_SKILLS_BY_YEAR


def create_table(input_dict, file_name):

    for year, key_skills in input_dict.items():
        str_key_skills_list = []
        for key_skill in key_skills:
            key_name, key_count = key_skill
            tmp_str = "{0}: {1}".format(key_name, key_count)
            str_key_skills_list.append(tmp_str)

        str_key_skills = ', '.join(str_key_skills_list)

        input_dict[year] = str_key_skills

    df = pd.DataFrame(list(input_dict.items()), columns=['Год', 'Ключевые навыки'])
    with open(file_name, 'w', encoding='utf-8-sig') as file:
        file.write(pretty_html_table.build_table(df, 'grey_light'))


if __name__ == '__main__':
    create_table(KEY_SKILLS_BY_YEAR_AND_KEY, '../../it_engeneer_vacancies/main/templates/main/key_skills_by_key.html')
    create_table(KEY_SKILLS_BY_YEAR, '../../it_engeneer_vacancies/main/templates/main/key_skills.html')
