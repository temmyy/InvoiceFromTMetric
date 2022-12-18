import requests
import pdfkit
from jinja2 import Environment, FileSystemLoader
import init


def get_time_entries(p):
    api_config = p['TMetric API']
    url_auth = api_config['url'] + '/user'
    headers = {key: api_config.get(key) for key in api_config}
    response_auth = requests.get(url_auth, headers=headers).json()

    active_account_id = str(response_auth.get('activeAccountId'))
    user_id = str(response_auth.get('id'))
    url_time = api_config['url'] + '/accounts/' + active_account_id + '/reports/projects'
    param_time = dict(
        accountId=active_account_id,
        startDate=p['General']['start_date'],
        endDate=p['General']['end_date'],
        userId=user_id
    )
    return requests.get(url_time, headers=headers, params=param_time).json()


def get_table_time(p):
    t = get_time_entries(p)
    for k in t:
        k['part'] = 0
        k['business_day'] = 0
        k['salary_amount'] = 0
        k['project']['project_description'] = get_project_description(p, k['project']['id'])
        p['total_seconds'] += k.get('totalSeconds')
    return t


def function_sort(element):
    return element['totalSeconds']


def distribute_on_best(t, q_best):
    t.sort(key=function_sort, reverse=True)
    if len(t) > q_best:
        amount_five = 0
        for k in t[0:q_best]:
            amount_five += k['totalSeconds']
        for k in t[q_best:]:
            for j in t[:q_best]:
                d = round((j['totalSeconds'] / amount_five), 2)
                j['totalSeconds'] += d * k['totalSeconds']
            amount_five += k['totalSeconds']
            k['totalSeconds'] = 0
        for k in range(len(t) - q_best):
            t.pop(len(t) - 1)


def control_of_totals(t, p):
    part = 0
    days = 0
    money = 0
    for k in t:
        part += k['part']
        days += k['business_day']
        money += k['salary_amount']
    last_item = t[p['quantity_in_invoice'] - 1]
    last_item['part'] = round(last_item['part'] + 1 - part, 2)
    last_item['business_day'] = round((last_item['business_day'] + p['business_day'] - days), 2)
    last_item['salary_amount'] = int(round(last_item['part'] * p['salary_amount'], 0))


def calculate_table_time(t, p):
    distribute_on_best(t, p['quantity_in_invoice'])
    for i in t:
        i['part'] = round(i['totalSeconds'] / params['total_seconds'], 2)
        i['business_day'] = round(i['part'] * params['business_day'], 1)
        i['salary_amount'] = round(i['part'] * params['salary_amount'])
    control_of_totals(t, params)


def get_project_description(p, project_id):
    project = p['projects_descriptions'].get(project_id)
    project_description = {}
    if project is None:
        project_description['name_ru'] = 'Неопределено (' + str(project_id) + ')'
        project_description['name_en'] = 'None'
    else:
        project_description['name_ru'] = project[0]
        project_description['name_en'] = project[1]
    return project_description


def print_table_to_console(t):
    print('_' * 76)
    print('Project' + ' ' * (60 - len('Project')), 'Part', 'Days', 'Money')
    print('_' * 76)
    s1 = 0
    s2 = 0
    s3 = 0
    for k in t:
        if k['totalSeconds'] == 0:
            continue
        project_description = k['project']['project_description']
        s1 += k['part']
        s2 += k['business_day']
        s3 += k['salary_amount']
        project_name_ru = project_description.get('name_ru')
        project_name_en = project_description.get('name_en')
        print(project_name_ru + ' ' * (60 - len(project_name_ru)),
              str(k['part']) + ' ',
              str(k['business_day']) + ' ',
              k['salary_amount'],
              '\n' + project_name_en)
        print('_ ' * 38)
    print('_' * 76)
    print(' ' * 60, str(round(s1, 2)) + ' ', str(round(s2, 1)), s3)


def print_invoice_to_pdf(t, p):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/" + p["General"]["invoice_template"])
    pdf_template = template.render(p)

    s = ''
    counter = 0
    for k in t:
        project_description = k['project']['project_description']
        counter += 1
        new_line = '''
              <tr>
                <td align="center">''' + str(counter) + '''</td>
                <td align="left"><b>''' + project_description.get('name_en') + '''</b><br>''' \
                   + project_description.get('name_ru') + '''</td>
                <td align="left">''' + str(k['part']) + '''<br>(business days: ''' + str(k['business_day']) \
                   + '''/''' + str(p.get('business_day')) + ''')</td>
                <td align="center">Month<br>Месяц</td>
                <td align="center">US$''' + str(p.get('salary_amount')) + '''</td>
                <td align="right">US$''' + str(k['salary_amount']) + '''</td>
              <tr>'''
        s += new_line
    pdf_template = pdf_template.replace('<!-- table_line -->', s)

    pdfkit.from_string(pdf_template, 'invoices/' + p.get('General').get('year')
                       + '.' + p.get('General').get('month') + '.pdf')


if __name__ == '__main__':

    params = init.init_invoice_params()
    table_time = get_table_time(params)

    calculate_table_time(table_time, params)
    print_table_to_console(table_time)
    print_invoice_to_pdf(table_time, params)
