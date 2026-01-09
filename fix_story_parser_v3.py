#!/usr/bin/env python
"""
修复 story_parser.py 的类结构问题 - v3版本
问题：_clean_response_string、_extract_status_from_response、_simple_fallback_match 三个方法缩进错误
"""

def fix_story_parser():
    with open('autoBMAD/epic_automation/story_parser.py', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 找到关键位置
    class_end = None
    methods_start = None
    methods_end = None

    for i, line in enumerate(lines):
        # 找到类的结束（_regex_fallback_parse_status方法之后）
        if line.strip() == "" and i > 395:
            # 检查前面是否是类方法
            prev_line = lines[i-1] if i > 0 else ""
            if "return \"Draft\"" in prev_line:
                # 找到"独立函数"注释
                if i + 5 < len(lines) and "# 独立函数" in lines[i+5]:
                    class_end = i
                    break

    # 找到方法开始位置
    methods_start = 463  # _clean_response_string 方法开始位置

    # 找到方法结束位置（_simple_fallback_match 方法结束）
    methods_end = None
    for i in range(methods_start, len(lines)):
        line = lines[i]
        if line.strip() == "# =========================================================================" and i > 600:
            methods_end = i
            break

    if methods_end is None:
        methods_end = 626  # 默认结束位置

    print(f"Class ends at line: {class_end}")
    print(f"Methods start at line: {methods_start}")
    print(f"Methods end at line: {methods_end}")

    # 提取各个部分
    before_class_methods = lines[:methods_start]
    bad_methods = lines[methods_start:methods_end]

    # 重新缩进这些方法（8个空格缩进）
    fixed_methods = []
    for line in bad_methods:
        if line.strip() == "":
            fixed_methods.append(line)
        elif line.strip().startswith("#"):
            fixed_methods.append(line)
        elif line.strip().startswith('def ') or line.strip().startswith('"""') or line.strip().startswith("'''"):
            # 方法定义和docstring，保持原样（已经是正确的缩进）
            fixed_methods.append(line)
        else:
            # 其他代码行，增加缩进
            fixed_methods.append("        " + line)

    # 重新组织
    new_lines = (
        before_class_methods +
        ['\n'] +
        fixed_methods +
        lines[methods_end:]
    )

    with open('autoBMAD/epic_automation/story_parser.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print("Fixed story_parser.py class structure - v3")
    print(f"Fixed methods: {len(fixed_methods)} lines")
    print("Successfully moved methods into SimpleStoryParser class")

if __name__ == '__main__':
    fix_story_parser()
