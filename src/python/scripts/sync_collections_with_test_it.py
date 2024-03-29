import sys
from glob import glob
import json
import configparser

from test_it_methods import create_work_item, update_work_item, create_section, \
    root_section_id, create_autotest, link_autotest_to_work_item, update_autotest

config = configparser.ConfigParser()
config.read('config.ini')
collections_path = config.get('CollectionsParams', 'path_with_collections')

def main():
    all_collections = glob('{}/*.postman_collection.json'.format(collections_path))

    for collection in all_collections:

        with open(collection, encoding='utf-8') as json_file:
            source_collection = json.load(json_file)

        collection_name = source_collection.get('info').get('name')
        collection_section = create_section(collection_name, root_section_id)
        scenarios = source_collection.get('item')

        for scenario in scenarios:
            scenario_name = scenario.get('name')
            cases = scenario.get('item')
            scenario_section = create_section(scenario_name, collection_section)
            for case in cases:
                case_name = case['name']
                case_steps = []
                for step in case['item']:
                    case_steps.append({'action': step['name']})

                if not case_exists(case_name):
                    global_id = create_work_item(case_name, case_steps, scenario_section)
                    autotest_id = create_autotest(global_id, case_name)
                    link_autotest_to_work_item(autotest_id, global_id)
                    case['name'] = '{}__{}'.format(global_id, case_name)

                else:
                    global_id = case_exists(case_name).get('global_id')
                    case_name = case_exists(case_name).get('name')
                    update_work_item(case_name, case_steps, global_id)
                    update_autotest(global_id, case_name)

        save_collection_to_file(collection, source_collection)


def case_exists(name):
    list_args = name.split("__")
    # FIXME: what if someone used separator without id
    if len(list_args) == 2:
        return {'global_id': list_args[0], 'name': list_args[1]}
    else:
        return False


def save_collection_to_file(filename, collection_as_dict):
    file = open(filename, 'w+', encoding='utf-8')
    file.write(json.dumps(collection_as_dict, ensure_ascii=False, indent='\t'))
    file.close()


if __name__ == '__main__':
    sys.stdout.write(str(main()))
    sys.stdout.flush()
