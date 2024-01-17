import datetime


def format_date(text):
    date = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S%z")
    return date.strftime("%Y")