import datetime
import dateparser


def is_date(string, date_format="%Y-%m-%d %H:%M:%S"):
    try:
        datetime.datetime.strptime(string, date_format)
        return True
    except ValueError:
        return False


def difference_to_string(delta):
    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    s = ""

    if days > 0:
        s += f"{days} дней "
    if hours > 0:
        s += f"{hours} часов "
    if minutes > 0:
        s += f"{minutes} минут "
    if seconds > 0:
        s += f"{seconds} секунд "

    return s.strip()


def parse_date_from_NL(date):
    parsed_date = dateparser.parse(date)

    if parsed_date:
        return parsed_date
    else:
        return None