import re


def extract_code(input_string):
    # Detect code blocks
    pattern = r'```(?:python)?\s(.*?)```'
    match = re.search(pattern, input_string, re.DOTALL)

    if match:
        # Found code block
        code = match.group(1)
    else:
        # No code block, assume pure code
        code = input_string

    return code
