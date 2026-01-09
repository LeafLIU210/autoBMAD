#!/usr/bin/env python
"""
修复 story_parser.py 的类结构问题 - 完整版本
"""

def fix_story_parser():
    with open('autoBMAD/epic_automation/story_parser.py', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 找到关键位置
    class_start = None
    normalize_start = None
    class_methods_start = None

    for i, line in enumerate(lines):
        if 'class SimpleStoryParser:' in line:
            class_start = i
        if 'def _normalize_story_status(status: str) -> str:' in line and normalize_start is None:
            normalize_start = i
        if '    def _clean_response_string' in line and class_methods_start is None:
            class_methods_start = i

    if class_start is None:
        print("Error: Could not find class definition")
        return

    if normalize_start is None:
        print("Error: Could not find _normalize_story_status function")
        return

    if class_methods_start is None:
        print("Error: Could not find class methods")
        return

    print(f"Class starts at line: {class_start + 1}")
    print(f"_normalize_story_status starts at line: {normalize_start + 1}")
    print(f"Class methods start at line: {class_methods_start + 1}")

    # 提取各个部分
    before_class = lines[:class_start]
    class_def = lines[class_start:normalize_start]
    class_methods = lines[class_methods_start:]
    after_class = lines[normalize_start:class_methods_start]

    # 找到类方法的结束位置（找到第一个非方法行）
    method_end = 0
    for i in range(len(class_methods)):
        line = class_methods[i]
        # 如果这行没有缩进（不是方法），这就是类方法的结束
        if line and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('#'):
            method_end = i
            break
    else:
        method_end = len(class_methods)

    actual_class_methods = class_methods[:method_end]
    remaining_code = class_methods[method_end:]

    # 重新组织
    new_lines = (
        before_class +
        class_def +
        ['\n'] +
        ['# =========================================================================\n'] +
        ['# 独立函数\n'] +
        ['# =========================================================================\n'] +
        ['\n'] +
        after_class +
        ['\n'] +
        actual_class_methods +
        remaining_code
    )

    with open('autoBMAD/epic_automation/story_parser.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print("Fixed story_parser.py class structure - v2")
    print(f"Before class: {len(before_class)} lines")
    print(f"Class definition: {len(class_def)} lines")
    print(f"Class methods: {len(actual_class_methods)} lines")
    print(f"Independent function: {len(after_class)} lines")
    print(f"Remaining code: {len(remaining_code)} lines")

if __name__ == '__main__':
    fix_story_parser()
