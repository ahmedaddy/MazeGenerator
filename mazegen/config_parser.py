import sys


def read_file(filepath: str) -> list[str]:
    array = []
    try:
        with open(filepath, 'r') as fd:
            array = fd.read().splitlines()
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        sys.exit(1)
    if len(array) == 0:
        print("No data read from file.")
        sys.exit(1)
    return array


def clean_lines(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        if line.strip().startswith('#'):
            continue
        if line.strip() == '':
            continue
        cleaned.append(line.strip())
    return cleaned


def parse_line(line: str) -> tuple[str, str]:
    if '=' not in line:
        print(f"Line '{line}' is not in the format 'key=value'.")
        sys.exit(1)
    key, value = line.split('=', 1)
    return key.strip(), value.strip()


def validate_and_convert(config: dict[str, str]) -> dict[str, any]:
    validated = {}
    mandatory_keys = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT',
                      'OUTPUT_FILE', 'PERFECT']
    for key, value in config.items():
        if key == 'WIDTH' or key == 'HEIGHT':
            try:
                validated[key] = int(value)
                if (validated[key] <= 0):
                    print(f"{key} must be a positive integer. Found \
'{value}'.")
                    sys.exit(1)
            except ValueError:
                print(f"Value for {key} must be an integer. Found '{value}'.")
                sys.exit(1)
        elif key == 'ENTRY' or key == 'EXIT':
            if (',' not in value):
                print(f"{key} must be in the format 'x,y'. Found '{value}'.")
                sys.exit(1)
            x_s, y_s = value.split(',', 1)
            try:
                x = int(x_s)
                y = int(y_s)
                if x < 0 or y < 0:
                    print(f"{key} coordinates must be non-negative integers. \
Found '{value}'.")
                    sys.exit(1)
                validated[key] = (x, y)
            except ValueError:
                print(f"{key} coordinates must be integers. Found '{value}'.")
                sys.exit(1)
        elif key == 'OUTPUT_FILE':
            if value == '':
                print(f"{key} cannot be empty.")
                sys.exit(1)
            validated[key] = value
        elif key == 'PERFECT':
            if value.lower() not in ['true', 'false']:
                print(f"{key} must be 'True' or 'False'. Found '{value}'.")
                sys.exit(1)
            else:
                if value.lower() == 'true':
                    validated[key] = True
                else:
                    validated[key] = False
        else:
            sys.exit(f"Unknown configuration key '{key}'.")
    for x_key in mandatory_keys:
        if x_key not in list(validated.keys()):
            print(f"Missing mandatory configuration key '{x_key}'.")
            sys.exit(1)
    width = validated['WIDTH']
    height = validated['HEIGHT']
    entry = validated['ENTRY']
    exit_ = validated['EXIT']
    if entry[0] < 0 or entry[0] >= width or entry[1] < 0 or entry[1] >= height:
        print(f"ENTRY {entry} is out of maze bounds ({width}x{height}).")
        sys.exit(1)
    if exit_[0] < 0 or exit_[0] >= width or exit_[1] < 0 or exit_[1] >= height:
        print(f"EXIT {exit_} is out of maze bounds ({width}x{height}).")
        sys.exit(1)
    if entry == exit_:
        print(f"ENTRY and EXIT must be different. Both are {entry}.")
        sys.exit(1)
    return validated


def parse_config(filepath: str) -> dict[str, any]:
    lines = read_file(filepath)
    cleaned_lines = clean_lines(lines)
    final_results = {}
    for line in cleaned_lines:
        key, value = parse_line(line)
        if key is not None and value is not None:
            final_results[key] = value
    validated_config = validate_and_convert(final_results)
    return validated_config
