import json

import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
base_url = config.get('TmsParams', 'test_it_base_url')
auth = {'Authorization': 'PrivateToken {}'.format(config.get('TmsParams', 'token'))}
project_id = config.get('TmsParams', 'project_id')
test_run_id = config.get('TmsParams', 'test_run_id')
configuration_id = config.get('TmsParams', 'configuration_id')
root_section_id = config.get('TmsParams', 'root_section_id')


def get_headers_with_auth(headers_dict):
    headers = auth.copy()
    headers.update(headers_dict)
    return headers


def log_message(url, response):
    return '\n url: %s\n status_code: %d\n response: %s' % (url, response.status_code, response.text)


def create_work_item(name, steps_dict, section_id):
    url = '{}/workItems'.format(base_url)
    body = {
        "attributes": {},
        "entityTypeName": "CheckLists",
        "links": [],
        "name": name,
        "postconditionSteps": [],
        "preconditionSteps": [],
        "priority": "Low",
        "projectId": project_id,
        "sectionId": section_id,
        "state": "Ready",
        "steps": steps_dict,
        "tags": [],
        "duration": 1000
    }

    response = requests.post(url=url, json=body, headers=get_headers_with_auth({'Content-Type': 'application/json'}))
    assert response.status_code == 201, log_message(url, response)
    return response.json()['globalId']


def get_work_item(global_id):
    url = '{}/workItems/{}'.format(base_url, global_id)
    response = requests.get(url=url, headers=get_headers_with_auth({'Accept': 'application/json'}))
    assert response.status_code == 200, log_message(url, response)

    response_as_json = response.json()
    return {'id': response_as_json['id'], 'sectionId': response_as_json['sectionId'], 'tags': response_as_json['tags']}


def update_work_item(name, steps_dict, global_id):
    try:
        get_info = get_work_item(global_id)
    except AssertionError:
        print('Кейс {} отмечен в postman-коллекции, как существующий, но в TestIT он отсутствует'.format(global_id))
        return

    url = '{}/workItems'.format(base_url)
    body = {
        "attachments": [],
        "attributes": {},
        "links": [],
        "name": name,
        "postconditionSteps": [],
        "preconditionSteps": [],
        "priority": "Low",
        "state": "Ready",
        "steps": steps_dict,
        "tags": get_info['tags'],
        "id": get_info['id'],
        "sectionId": get_info['sectionId'],
        "duration": 1000
    }

    response = requests.put(url=url, json=body, headers=get_headers_with_auth({'Content-Type': 'application/json'}))
    assert response.status_code == 204, log_message(url, response)


def create_section(name, parent_section_id):
    url = '{}/sections'.format(base_url)
    body = {
        "name": name,
        "projectId": project_id,
        "parentId": parent_section_id
    }

    response = requests.post(url=url, json=body, headers=get_headers_with_auth({'Content-Type': 'application/json'}))

    if response.status_code == 409 and ('already exists' in response.json().get('error').get('key')):
        sections = get_sections()

        for section in sections:
            if section.get('name') == name and section.get('parentId') == parent_section_id:
                return section.get('id')

    assert response.status_code == 201, log_message(url, response)
    return response.json()['id']


def get_sections():
    url = '{}/projects/{}/sections'.format(base_url, project_id)
    response = requests.get(url=url, headers=get_headers_with_auth({'Accept': 'application/json'}))
    return response.json()


def create_autotest(external_id, name):
    url = '{}/autoTests'.format(base_url)
    body = {
        "externalId": external_id,
        "name": name,
        "projectId": project_id,
        "namespace": "Autotests",
        "classname": "Postman"
    }
    response = requests.post(url=url, json=body, headers=get_headers_with_auth({'Content-Type': 'application/json'}))
    assert response.status_code == 201, log_message(url, response)

    return response.json().get('globalId')


def update_autotest(external_id, name):
    id = get_autotest_by_external_id(external_id)

    url = '{}/autoTests'.format(base_url)
    body = {
        "id": id,
        "externalId": external_id,
        "name": name,
        "projectId": project_id,
        "namespace": "Autotests",
        "classname": "Postman"
    }
    response = requests.put(url=url, json=body, headers=get_headers_with_auth({'Content-Type': 'application/json'}))
    assert response.status_code == 204, log_message(url, response)


def link_autotest_to_work_item(autotest_id, work_item_id):
    url = '{}/autoTests/{}/workItems'.format(base_url, autotest_id)
    body = {
        "id": work_item_id
    }
    response = requests.post(url=url, json=body, headers=get_headers_with_auth({'Content-Type': 'application/json'}))
    assert response.status_code == 204, log_message(url, response)


def get_autotest_by_external_id(external_id):
    url = '{}/autoTests'.format(base_url)
    params = {'projectId': project_id, 'externalId': external_id}
    response = requests.get(url=url, params=params, headers=get_headers_with_auth({'Accept': 'application/json'}))
    assert response.status_code == 200, log_message(url, response)
    return response.json()[0].get('id')


def get_all_autotests_in_project():
    url = '{}/autoTests'.format(base_url)
    if(project_id==None):
        raise Exception
    params = {'projectId': project_id}
    response = requests.get(url=url, params=params, headers=get_headers_with_auth({'Accept': 'application/json'}))
    assert response.status_code == 200, log_message(url, response)
    return response.json()


def delete_autotest_by_global_id(global_id):
    url = '{}/autoTests/{}'.format(base_url, global_id)
    response = requests.delete(url=url, headers=get_headers_with_auth({}))
    assert response.status_code == 204, log_message(url, response)


def delete_all_autotests_in_project():
    autotests = get_all_autotests_in_project()
    for autotest in autotests:
        global_id = autotest.get('globalId')
        delete_autotest_by_global_id(global_id)


def set_test_result(external_id, status, traces):
    url = '{}/testRuns/{}/testResults'.format(base_url, test_run_id)
    body = [
        {
            "configurationId": configuration_id,
            "autoTestExternalId": external_id,
            "outcome": status,
            "startedOn": "2021-09-22T08:38:45.5374963+00:00",
            "completedOn": "2021-09-22T08:38:45.5374963+00:00",
            "traces": traces if traces is not None else ""
        }
    ]

    response = requests.post(url=url, json=body,
                             headers=get_headers_with_auth({'Content-Type': 'application/json'}))
    assert response.status_code == 200, log_message(url, response)

