#! coding: utf8
import json
from pathlib import Path
import argparse

from test_it_methods import set_test_result


def find_failures(json_obj):
    count_of_failures = int(json_obj['Run']['Stats']['Assertions']['failed'])
    # count_of_failures = int(json_obj['Run']['Stats']['Requests']['failed']) + \
    #                     int(json_obj['Run']['Stats']['Assertions']['failed'])
    failures_list = json_obj['Run']['Failures']
    failures_list_of_assertions = []
    failures_list_of_another_errors = []

    traces = '<html><p style="color: #ff0000"><big>Всего ошибок в проверках: {}</big></p></html>'.format(str(count_of_failures))
    for fa in failures_list:
        if fa.get('Error').get('Test') is not None:
            failures_list_of_assertions.append(fa)

    for f in range(len(failures_list_of_assertions)):
        failure = failures_list[f - 1]
        step_name = failure.get('Source').get('Name')
        test_name = failure.get('Error').get('Test')
        error_message = failure.get('Error').get('Message')

        trace_format = '<html><p style="color: #ff0000"><big>{}.AssertionError</big></p><br>	<p style="color: #ffff00">Шаг: </p><p>{}</p><br><p style="color: #ffff00">Проверка: </p><p>{}</p><br><p style="color: #ffff00">Ошибка: </p><p>{}</p><br></html>'.format(f + 1, step_name,
                                                                                           test_name,
                                                                                           error_message)

        traces = '<html>{}<br><br>{}</html>'.format(traces, trace_format)

    for fa in failures_list:
        if fa.get('Error').get('Test') is None:
            failures_list_of_another_errors.append(fa)
    traces = '{}<html><p style="color: #ff0000"><big>Всего прочих ошибок: {}</big></p><br></html>'.format(traces, str(len(failures_list_of_another_errors)))

    for f in range(len(failures_list_of_another_errors)):
        failure = failures_list[f - 1]
        step_name = failure.get('Source').get('Name')
        error_message = failure.get('Error').get('Message')
        trace_format = '<html><p style="color: #ff0000"><big>{}. Error </big></p><br>	<p style="color: #ffff00">Шаг: </p><p>{}</p><br><p style="color: #ffff00">Ошибка: </p><p>{}</p><br></html>'.format(f + 1, step_name, error_message)
        traces = '<html>{}<br><br>{}</html>'.format(traces, trace_format)

    return traces


def find_result_of_test(search_path):
    res = dict()

    json_list = list(Path(search_path).glob('*.json'))
    if len(json_list) == 0:
        return None
    json_report = json_list[0]

    with open(json_report, encoding='utf-8') as json_file:
        json_obj = json.load(json_file)
        status = None

        if (json_obj['Run']['Stats']['Requests']['failed'] == 0) & (
                json_obj['Run']['Stats']['Assertions']['failed'] == 0):
            status = "Passed"
        else:
            status = "Failed"
            res['traces'] = find_failures(json_obj)

    res['status'] = status
    print(res.get('traces'))
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='filename .postman_collection.json')
    parser.add_argument('-i', '--input', type=Path, required=False, default='./collections/temp/newman',
                        help='collections/archive path')

    args = parser.parse_args()
    search_path = args.input
    external_id = args.filename.split(".")[0]
    result = find_result_of_test(search_path.as_posix())
    set_test_result(external_id, result.get('status'), result.get('traces'))
