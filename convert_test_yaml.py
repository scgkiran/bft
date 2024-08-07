import yaml
import sys


def convert_yaml(input_file, output_file):
    with open(input_file, 'r') as file:
        old_yaml_data = yaml.safe_load(file)

    output = [
        "### SUBSTRAIT_SCALAR_TEST: 1.0\n",
        f"### SUBSTRAIT_INCLUDE: {old_yaml_data['base_uri']}\n"
    ]
    function = old_yaml_data['function']

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

        # if args.value is array and if it has 'None' value, then replace it with 'Null'
        for arg in args:
            if type(arg['value']) is list:
                arg['value'] = f"[{', '.join(['Null' if x is None else str(x) for x in arg['value']])}]"

        # Construct the testcases using new format
        if args and result:
            args_str = ', '.join(
                [f"{arg['value']}::{arg['type']}" for arg in args])
            if result.get('special') is None:
                value = 'Null' if result['value'] is None else result['value']
                result_str = f"{value}::{result['type']}"
            else:
                result_str = result['special']
            test = {f"{args_str}": result_str}
            test_group['tests'].append(test)

        # Add the test group to the list of cases
        if group_name in groups:
            groups[group_name]['tests'] += test_group['tests']
        else:
            groups[group_name] = test_group

    for _, group_tests in groups.items():
        output.append(f"\n# {group_tests['group']}: {group_tests['description']}\n")
        option_str = get_option_str(group_tests.get('options', None))
        for test in group_tests['tests']:
            for arg_list, result in test.items():
                output.append(f"{function}({arg_list}){option_str} = {result}\n")

    with open(output_file, 'w') as file:
        file.writelines(output)
    print(f"Conversion complete. The new format has been saved to '{output_file}'.")


def get_option_str(options):
    if options is None:
        return ''
    option_strs = [f"{k}:{v}" for k, v in options.items()]
    return f" [{', '.join(option_strs)}]"


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


if __name__ == '__main__':
    main()
