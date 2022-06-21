import json
import uuid
from pathlib import Path
import configparser

def generate_separate_collection(collection, base_scenario):
    """
    :param collection: source collection that includes all cases and base info
    :param base_scenario: scenario that includes single case
    :return: collection with single case based on scenario extracted from collection
    """
    result_collection_uuid = str(uuid.uuid4())
    # common arguments for collection that will be inherited from source collection
    common = {}
    if 'info' in collection:
        common['info'] = collection.get('info')
        common['info']['_postman_id'] = result_collection_uuid
    if 'auth' in collection:
        common['auth'] = collection.get('auth')
    if 'event' in collection:
        common['event'] = collection.get('event')
    if 'variable' in collection:
        common['variable'] = collection.get('variable')
    common['item'] = []
    common['item'].append(base_scenario)

    return common


def save_collection_to_file(col, output_file):
    file = open(output_file, 'w+', encoding='utf-8')
    file.write(json.dumps(col, ensure_ascii=False, indent=4))
    file.close()


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('config.ini')

    paths_to_collections = list(Path(config.get('CollectionsParams', 'path_with_collections')).glob('*.json'))

    for path in paths_to_collections:
        with open(path, encoding='utf-8') as json_file:
            source_collection = json.load(json_file)

        collection_name = source_collection.get('info').get('name')
        # scenarios are the first level of folders in collection
        # scenarios also contain cases that will be executed
        scenarios = source_collection.get('item')

        for scenario in scenarios:
            cases = scenario.get('item')
            for case in cases:
                # cases have naming conventions
                # each case should start with prefix containing id and separator '__'
                # example: 123__Name
                case_id = case['name'].split('__')[0]
                result_scenario = {'name': collection_name,
                                   'item': [{'name': scenario.get('name'), 'item': []}]}
                result_scenario.get('item')[0].get('item').append(case)
                result_collection = generate_separate_collection(source_collection, result_scenario)

                result_file = Path(config.get('CollectionsParams', 'path_for_single_collections')).joinpath(f'{case_id}.postman_collection.json')
                save_collection_to_file(result_collection, result_file.as_posix())
