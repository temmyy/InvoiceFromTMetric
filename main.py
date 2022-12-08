import requests
import datetime
import pdfkit
from jinja2 import Environment, FileSystemLoader

import init


def function_sort(element):
    return element[1]


def distribute_on_best(q_best):
    list_time = [[j, table_time.get(j)[0]] for j in table_time]  # fill list and sort
    list_time.sort(key=function_sort, reverse=True)

    if len(list_time) > q_best:
        amount_five = 0
        for k in list_time[0:q_best]:
            amount_five += k[1]
        for k in list_time[q_best:]:
            for j in list_time[:q_best]:
                d = round((j[1] / amount_five), 2)
                j[1] += d * k[1]
            amount_five += k[1]
            k[1] = 0
        for k in list_time:
            if k[1] == 0:
                table_time.pop(k[0])
            else:
                table_time.get(k[0])[0] = k[1]


def get_project_description(project_id):
    project = projects_description.get(project_id)
    project_description = {}
    if project is None:
        project_description['name_ru'] = 'Неопределено (' + str(project_id) + ')'
        project_description['name_en'] = 'None'
    else:
        project_description['name_ru'] = project[0]
        project_description['name_en'] = project[1]
    return project_description


def print_table():
    print('_' * 76)
    print('Project' + ' ' * (60 - len('Project')), 'Part', 'Days', 'Money')
    print('_' * 76)
    s1 = 0
    s2 = 0
    s3 = 0
    for k in table_time.items():
        if k[1][0] == 0:
            continue
        project_description = get_project_description(k[0])
        s1 += k[1][1]
        s2 += k[1][2]
        s3 += k[1][3]
        project_name_ru = project_description.get('name_ru')
        project_name_en = project_description.get('name_en')
        print(project_name_ru + ' ' * (60 - len(project_name_ru)),
              str(k[1][1]) + ' ',
              str(k[1][2]) + ' ',
              k[1][3],
              '\n' + project_name_en)
        print('_ ' * 38)
    print('_' * 76)
    print(' ' * 60, str(round(s1, 2)) + ' ', str(round(s2, 1)), s3)


def control_of_totals(p):
    part = 0
    days = 0
    money = 0
    for k in table_time.values():
        part += k[1]
        days += k[2]
        money += k[3]
    last_item = list(table_time.values())[p['quantity_in_invoice'] - 1]
    last_item[1] = round(last_item[1] + 1 - part, 2)
    last_item[2] = round((last_item[2] + p['business_day'] - days), 2)
    last_item[3] = int(round(last_item[1] * p['salary_amount'], 0))


def get_time_entries(p):
    api_config = p['TMetric API']
    url_auth = 'https://app.tmetric.com/api/v3/user'
    headers = {key: api_config.get(key) for key in api_config}
    response_auth = requests.get(url_auth, headers=headers).json()

    active_account_id = str(response_auth.get('activeAccountId'))
    user_id = str(response_auth.get('id'))
    url_time = 'https://app.tmetric.com/api/v3/accounts/' + active_account_id + '/timeentries'
    param_time = dict(
        accountId=active_account_id,
        startDate=p['General']['start_date'],
        endDate=p['General']['end_date'],
        userId=user_id
    )
    return requests.get(url_time, headers=headers, params=param_time).json()


def fill_table_time(p):
    response_time = get_time_entries(p)
    for k in response_time:
        project_id = k.get('project').get('id')
        end_time = k.get('endTime')
        if end_time is None:
            end_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        delta_time = init.string_to_date(end_time) - init.string_to_date(k.get('startTime'))
        seconds = delta_time.days * 24 * 60 * 60 + delta_time.seconds
        if project_id not in table_time:
            table_time[project_id] = [0, 0, 0, 0]
        table_time[project_id][0] += seconds
        p['total_seconds'] += seconds


def fill_projects_description():
    with open('projects_description.txt') as file:
        for text_line in file.readlines():
            if text_line.startswith('#'):
                continue
            line = text_line.strip().split('|')
            projects_description[int(line[0])] = [line[1], line[2]]


def print_invoice_to_pdf(p):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/Invoice_template_EN.html")
    pdf_template = template.render(p)

    s = ''
    counter = 0
    for k in table_time.items():
        project_description = get_project_description(k[0])
        counter += 1
        new_line = '''
              <tr>
                <td align="center">''' + str(counter) + '''</td>
                <td align="left"><b>''' + project_description.get('name_en') + '''</b><br>''' \
                   + project_description.get('name_ru') + '''</td>
                <td align="left">''' + str(k[1][1]) + '''<br>(business days: ''' + str(k[1][2]) \
                   + '''/''' + str(p.get('business_day')) + ''')</td>
                <td align="center">Month<br>Месяц</td>
                <td align="center">US$''' + str(p.get('salary_amount')) + '''</td>
                <td align="right">US$''' + str(k[1][3]) + '''</td>
              <tr>'''
        s += new_line
    pdf_template = pdf_template.replace('<!-- table_line -->', s)

    pdfkit.from_string(pdf_template, 'invoices/' + p.get('GeneralForPrint').get('year')
                       + '.' + p.get('GeneralForPrint').get('month') + '.pdf')


if __name__ == '__main__':

    params = init.init_invoice_params()

    table_time = {}
    projects_description = {}

    fill_projects_description()
    fill_table_time(params)
    distribute_on_best(params['quantity_in_invoice'])

    for i in table_time.values():
        i[1] = round(i[0] / params['total_seconds'], 2)
        i[2] = round(i[1] * params['business_day'], 1)
        i[3] = round(i[1] * params['salary_amount'])

    control_of_totals(params)
    print_table()

    print_invoice_to_pdf(params)
