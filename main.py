import requests
import datetime
import calendar


def init():

    p = {}
    with open('config.txt') as config:
        for r in config.readlines():
            if r.startswith('apiKey'):
                p['apiKey'] = r[7:-1]
                p['headers'] = {"Authorization": "Bearer " + p['apiKey'], "accept": "text/json"}
            elif r.startswith('salary'):
                p['salary'] = int(r[7:-1])
            elif r.startswith('quantityInInvoice'):
                p['quantityInInvoice'] = int(r[18:-1])
        p['businessDay'] = int(input('Количество рабочих дней: '))

        year = str(input('Год в формате [2021]: '))
        month = str(input('Месяц в формате [08]: '))
        start_date = string_to_date(year + '-' + month + '-01T00:00:00')
        days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = start_date + datetime.timedelta(days=days_in_month) - datetime.timedelta(seconds=1)

        p['startDate'] = start_date.strftime('%Y-%m-%dT%H:%M:%S')
        p['endDate'] = end_date.strftime('%Y-%m-%dT%H:%M:%S')

    return p


def string_to_date(date_in_string):
    return datetime.datetime.strptime(date_in_string, "%Y-%m-%dT%H:%M:%S")


def function_sort(element):
    return element[1]


def distribute_on_best(table_time, q_best):
    list_time = [[j, table_time.get(j)[0]] for j in table_time]  # заполним список и отсортируем
    list_time.sort(key=function_sort, reverse=True)

    if len(list_time) > q_best:
        amount_five: int = 0  # сумма лучших пяти, для определения доли лучших пяти
        for k in list_time[0:q_best]:
            amount_five += k[1]
        for k in list_time[q_best:]:  # обходим тех, кто не вошёл в лучшую пятёрку
            for j in list_time[:q_best]:  # распределяем по пятёрке лучших в долях
                d = round((j[1] / amount_five), 2)
                j[1] += d * k[1]
            amount_five += k[1]
            k[1] = 0
        for k in list_time:
            table_time.get(k[0])[0] = k[1]


def print_table(table_time):
    print('_' * 46)
    print('Проект' + ' ' * (30 - len('Проект')), 'Доля', 'Дней', 'Деньги')
    print('_' * 46)
    s1 = 0
    s2 = 0
    s3 = 0
    for k in table_time.items():
        if k[1][0] == 0:
            continue
        project_name = projects.get(k[0])
        s1 += k[1][1]
        s2 += k[1][2]
        s3 += k[1][3]
        print(project_name + ' ' * (30 - len(project_name)), str(k[1][1]) + ' ', str(k[1][2]) + ' ', k[1][3])
    print('_' * 46)
    print(' ' * 30, str(round(s1, 2)) + ' ', str(round(s2, 1)), s3)


def control_of_totals(table_time, p):
    part = 0
    days = 0
    money = 0
    for k in table_time.values():
        part += k[1]
        days += k[2]
        money += k[3]
    last_item = list(table_time.values())[p['quantityInInvoice']]
    last_item[1] = round(last_item[1] + 1 - part, 2)
    last_item[2] = round((last_item[2] + p['businessDay'] - days), 2)
    last_item[3] = round(last_item[1] * p['salary'], 0)


def get_time_entries(p):
    url_auth = 'https://app.tmetric.com/api/v3/user'
    response_auth = requests.get(url_auth, headers=p['headers']).json()

    active_account_id = str(response_auth.get('activeAccountId'))
    user_id = str(response_auth.get('id'))
    url_time = 'https://app.tmetric.com/api/v3/accounts/' + active_account_id + '/timeentries'
    param_time = dict(
        accountId=active_account_id,
        startDate=p['startDate'],
        endDate=p['endDate'],
        userId=user_id
    )
    return requests.get(url_time, headers=params['headers'], params=param_time).json()


if __name__ == '__main__':

    params = init()
    response_time = get_time_entries(params)

    table_time = {}
    projects = {}
    amount_seconds = 0

    for k in response_time:
        project_id = k.get('project').get('id')
        projectName = k.get('project').get('name')
        if project_id not in projects:
            projects[project_id] = projectName
        deltaTime = string_to_date(k.get('endTime')) - string_to_date(k.get('startTime'))
        seconds = deltaTime.days * 24 * 60 * 60 + deltaTime.seconds
        if project_id not in table_time:
            table_time[project_id] = [0 for n in range(0, 4)]
        table_time[project_id][0] += seconds
        amount_seconds += seconds

    distribute_on_best(table_time, params['quantityInInvoice'])

    for i in table_time.values():
        i[1] = round(i[0] / amount_seconds, 2)
        i[2] = round(i[1] * params['businessDay'], 1)
        i[3] = round(i[1] * params['salary'])

    control_of_totals(table_time, params)
    print_table(table_time)
