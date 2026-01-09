#!/usr/bin/env python
"""
修复 story_parser.py 的类结构问题
"""

def fix_story_parser():
    with open('autoBMAD/epic_automation/story_parser.py', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 找到类开始的位置
    class_start = None
    normalize_start = None

    for i, line in enumerate(lines):
        if 'class SimpleStoryParser:' in line:
            class_start = i
        if 'def _normalize_story_status(status: str) -> str:' in line:
            normalize_start = i
            break

    if class_start is None:
        print("Error: Could not find class definition")
        return

    if normalize_start is None:
        print("Error: Could not find _normalize_story_status function")
        return

    # 提取类之前的部分（常量定义等）
    before_class = lines[:class_start]

    # 提取类部分（从 class 定义到 _normalize_story_status 之前）
    class_lines = lines[class_start:normalize_start]

    # 提取 _normalize_story_status 及其后的部分
    after_class = lines[normalize_start:]

    # 重新组织类部分
    new_class_lines = []
    in_class = True

    for line in class_lines:
        stripped = line.lstrip()

        # 如果这行开始了一个新的顶级定义，停止处理类
        if in_class and stripped and not line.startswith(' ') and not line.startswith('\t'):
            in_class = False
            break

        new_class_lines.append(line)

    # 重新写入文件
    new_lines = (
        before_class +
        new_class_lines +
        ['\n'] +
        ['# =========================================================================\n'] +
        ['# 独立函数\n'] +
        ['# =========================================================================\n'] +
        ['\n'] +
        after_class
    )

    with open('autoBMAD/epic_automation/story_parser.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print("Fixed story_parser.py class structure")

if __name__ == '__main__':
    fix_story_parser()
