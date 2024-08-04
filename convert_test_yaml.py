import yaml
import sys


def convert_yaml(input_file, output_file):
    with open(input_file, 'r') as file:
        old_yaml_data = yaml.safe_load(file)

    new_yaml_data = {
        'base_uri': old_yaml_data['base_uri'],
        'function': old_yaml_data['function'],
        'cases': []
    }

    description_map = {}
    groups = {}
    for case in old_yaml_data['cases']:
        group = case.get('group', {})
        if isinstance(group, dict):
            group_name = group.get('id', 'basic')
            description = group.get('description', '')
            description_map[group_name] = description
        else:
            group_name = group
            description = ''

        options = case.get('options', None)

        # Handle tests in the old format
        test_group = {
            'group': group_name,
            'description': description,
        }

        # Add options to test_group if present
        if options:
            test_group['options'] = options
            options_str = ', '.join([f"{key} with {value}" for key, value in options.items()])
            if test_group['description'] == '':
                test_group['description'] = f"{description_map.get(group_name, '')} tests: {options_str}"
            group_name = f"{test_group['group']} tests: {options_str}"
            # test_group['group'] = group_name

        test_group['tests'] = []
        # Handle each test case
        args = case.get('args', [])
        result = case.get('result', {})

        # Construct the testcases using new format
        if args and result:
            args_str = ', '.join(
                [f"{arg['value']}|{arg['type']}" for arg in args])
            if result.get('special') is None:
                result_str = f"{result['value']}|{result['type']}"
            else:
                result_str = result['special']
            test = {f"({args_str})": result_str}
            test_group['tests'].append(test)

        # Add the test group to the list of cases
        if group_name in groups:
            groups[group_name]['tests'] += test_group['tests']
            # if options is None or test_group.get('options') is groups[group_name]['options']:
            #     groups[group_name]['tests'] += test_group['tests']
            # else:
            #     test_group_name = f"{group_name} tests: {options_str}"
            #     test_group['group'] = test_group_name
            #     if test_group['description'] == '':
            #         test_group['description'] = f"{groups[group_name]['description']} tests: {options_str}"
            #     groups[test_group_name] = test_group
        else:
            groups[group_name] = test_group

    for _, group_tests in groups.items():
        new_yaml_data['cases'].append(group_tests)

    with open(output_file, 'w') as file:
        yaml.dump(new_yaml_data, file, sort_keys=False, default_flow_style=False)

    print(f"Conversion complete. The new format has been saved to '{output_file}'.")


input_files = [
    'cases/arithmetic/add.yaml',
    'cases/arithmetic/max.yaml',
    'cases/arithmetic_decimal/power_decimal.yaml',
    'cases/datetime/lt_datetime.yaml',
]


def main():
    for input_path in input_files:
        input_file = input_path.split('/')[-1]
        output_path = f"/Users/chandra/junk/{input_file}"
        convert_yaml(input_path, output_path)

    with open('cases_new/arithmetic/add.yaml', 'r') as file:
        yam_data = yaml.safe_load(file)

    print(yam_data)


if __name__ == '__main__':
    main()
