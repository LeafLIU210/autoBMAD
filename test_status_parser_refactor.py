#!/usr/bin/env python
"""验证 StatusParser 重构是否成功"""

import sys

def test_imports():
    """测试导入"""
    print("测试 1: 导入模块...")
    try:
        from status_parser import SimpleStatusParser, StatusParser, parse_story_status
        print("  [OK] 成功导入所有模块")
        print(f"  [OK] SimpleStatusParser: {SimpleStatusParser}")
        print(f"  [OK] StatusParser 是 SimpleStatusParser 的别名: {StatusParser is SimpleStatusParser}")
        return True
    except Exception as e:
        print(f"  [ERROR] 导入失败: {e}")
        return False

def test_class_creation():
    """测试类创建"""
    print("\n测试 2: 创建解析器实例...")
    try:
        from status_parser import SimpleStatusParser
        parser = SimpleStatusParser()
        print(f"  [OK] 成功创建 SimpleStatusParser 实例")
        print(f"  [OK] SDK wrapper: {parser.sdk_wrapper}")
        return True
    except Exception as e:
        print(f"  [ERROR] 创建实例失败: {e}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n测试 3: 向后兼容性...")
    try:
        from status_parser import StatusParser, parse_story_status
        
        # 测试 StatusParser 别名
        parser = StatusParser()
        print(f"  [OK] StatusParser 别名工作正常")
        
        # 测试 parse_story_status 函数
        test_content = "## Status\n**Status**: Ready for Review"
        result = parse_story_status(test_content)
        print(f"  [OK] parse_story_status 函数可调用")
        
        return True
    except Exception as e:
        print(f"  [ERROR] 向后兼容性测试失败: {e}")
        return False

def main():
    print("=" * 60)
    print("StatusParser 重构验证测试")
    print("=" * 60)
    
    results = []
    results.append(test_imports())
    results.append(test_class_creation())
    results.append(test_backward_compatibility())
    
    print("\n" + "=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    if all(results):
        print("\n[SUCCESS] 所有测试通过！StatusParser 重构成功。")
        return 0
    else:
        print("\n[FAILED] 部分测试失败。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
