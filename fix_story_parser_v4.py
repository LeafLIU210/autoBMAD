#!/usr/bin/env python
"""
修复 story_parser.py 的类结构问题 - v4版本
更精确的修复：正确将方法移到类内部
"""

def fix_story_parser():
    with open('autoBMAD/epic_automation/story_parser.py', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 找到关键位置
    class_end = None
    methods_start = 463  # _clean_response_string 方法开始位置
    methods_end = None

    # 找到类的结束位置（在独立函数注释之前）
    for i in range(395, 410):
        if i < len(lines) and "# 独立函数" in lines[i]:
            class_end = i
            break

    # 找到方法结束位置
    for i in range(methods_start, len(lines)):
        line = lines[i]
        if line.strip() == "# =========================================================================" and i > 600:
            methods_end = i
            break

    if methods_end is None:
        methods_end = 626

    print(f"Class ends at line: {class_end}")
    print(f"Methods start at line: {methods_start}")
    print(f"Methods end at line: {methods_end}")

    # 提取各个部分
    before_class_methods = lines[:methods_start]
    bad_methods = lines[methods_start:methods_end]

    # 重新缩进这些方法（4个空格缩进，对应类内部的8个空格）
    fixed_methods = []
    for line in bad_methods:
        if line.strip() == "":
            fixed_methods.append(line)
        elif line.strip().startswith("#"):
            fixed_methods.append(line)
        else:
            # 去掉当前的缩进，然后加上4个空格
            stripped = line.lstrip()
            fixed_methods.append("    " + stripped)

    # 重新组织
    new_lines = (
        before_class_methods +
        ['\n'] +
        fixed_methods +
        lines[methods_end:]
    )

    with open('autoBMAD/epic_automation/story_parser.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print("Fixed story_parser.py class structure - v4")
    print(f"Fixed methods: {len(fixed_methods)} lines")

if __name__ == '__main__':
    fix_story_parser()
