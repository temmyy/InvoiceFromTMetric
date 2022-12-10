import datetime
import calendar
import configparser
import os
from sys import argv


def init_invoice_params():

    # init variable parametrs
    try:
        script_name, year, month, business_day, invoice_number, conf_name = argv
    except:
        year = str(datetime.date.today().year)
        month = str(datetime.date.today().month)
        business_day = '19'
        today = datetime.date.today()
        invoice_number = 31 + (today.year * 12 + today.month) - (2022 * 12 + 10)
        conf_name = choose_conf()

    start_date = string_to_date(year + '-' + month + '-01T00:00:00')
    days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date + datetime.timedelta(days=days_in_month) - datetime.timedelta(seconds=1)

    # read config
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read("conf/" + conf_name)
    # add variable parametrs
    config['General']['business_day'] = business_day
    config['General']['invoice_number'] = str(invoice_number)
    config['General']['start_date'] = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    config['General']['end_date'] = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    config['General']['year'] = year
    config['General']['month'] = month
    config['General']['month_en'] = get_month_name(datetime.datetime.now().month, 0)
    config['General']['month_ru'] = get_month_name(datetime.datetime.now().month, 1)
    config['General']['day'] = str(datetime.datetime.now().day)

    # init params like object
    invoice_params = {'total_seconds': 0, 'quantity_in_invoice': int(config['General']['quantity_in_invoice']),
                      'business_day': int(config['General']['business_day']),
                      'salary_amount': int(config['General']['salary_amount'])}

    # add all parameters from config
    for section in config.sections():
        invoice_params[section] = {key: config[section].get(key) for key in config[section]}

    return invoice_params


def get_month_name(m, t=0):
    month_ru = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']
    month_en = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December']
    if t == 0:
        return month_en[int(m) - 1]
    else:
        return month_ru[int(m) - 1]


def string_to_date(date_in_string):
    return datetime.datetime.strptime(date_in_string, "%Y-%m-%dT%H:%M:%S")


def choose_conf():
    # looking for config
    configs = look_config()
    if len(configs) == 1:
        return list(configs[0].values())[0]
    else:
        print("Please, select config (enter number):")
        for i in range(len(configs)):
            print(i+1, ') ' + list(configs[i].keys())[0])
        conf_num = int(input()) - 1
        return list(configs[conf_num].values())[0]


def look_config():
    confs = []
    for file in os.listdir(os.getcwd()+'/conf'):
        if file.endswith(".ini"):
            confs.append({get_conf_alias(file): file})
    return confs


def get_conf_alias(file):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read("conf/" + file)
    return config.get('General', 'conf_alias', fallback=file)
