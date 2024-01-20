import wordcloud
from parsing.parsed_info.parsed_key_skills import KEY_SKILLS_BY_YEAR_AND_KEY, KEY_SKILLS_BY_YEAR
import matplotlib.pyplot as plt


def create_wordcloud(input_dict, file_name):
    tmp_dict = {}

    for key_skills in input_dict.values():
        for key_skill in key_skills:
            key_name, key_count = key_skill
            tmp_dict[key_name] = key_count
    word_cloud = wordcloud.WordCloud(width=700, height=500, background_color='#2c2c2c').generate_from_frequencies(tmp_dict)
    plt.imshow(word_cloud).write_png(file_name)


if __name__ == '__main__':
    create_wordcloud(KEY_SKILLS_BY_YEAR_AND_KEY,
                     '../../it_engeneer_vacancies/main/static/main/img/key_skills_by_key.png')
    create_wordcloud(KEY_SKILLS_BY_YEAR,
                     '../../it_engeneer_vacancies/main/static/main/img/key_skills.png')
