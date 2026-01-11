# 测试文件：包含各种代码质量问题


def calculate_sum(a,b):  # E225: missing whitespace around operator
    unused_var = 42  # F841: assigned but never used
    result=a+b  # E225: missing whitespace around operator
    return result

# E303: too many blank lines



def process_data(data):
    if data is None:  # E702: multiple statements on one line (if this were the case)
        return []

    result = []
    for item in data:
        result.append(item)

    # E501: line too long (this line exceeds the typical 88 character limit for code formatting and demonstrates the ruff formatting functionality we just implemented in the workflow integration system that combines basedpyright type checking with ruff linting and formatting capabilities)
    return result

class ExampleClass:
    def __init__(self):
        self.value = 0

    def get_value(self):
        return self.value