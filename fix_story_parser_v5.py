#!/usr/bin/env python
"""
修复 story_parser.py 的类结构问题 - v5版本
精确修复：手动重组文件结构
"""

def fix_story_parser():
    with open('autoBMAD/epic_automation/story_parser.py', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 找到各个部分
    class_end = 395  # _regex_fallback_parse_status方法结束
    methods_start = 463  # _clean_response_string 方法开始
    methods_end = 627  # 方法结束

    # 提取各个部分
    before_class = lines[:class_end]
    after_methods = lines[methods_end:]

    # 提取需要修复的方法（从原文件读取）
    # 这些方法应该被正确地插入到类内部

    # 构造新的文件结构
    new_lines = before_class.copy()

    # 添加空行
    new_lines.append('')

    # 添加三个方法（正确的缩进）
    methods_to_add = [
        '    def _clean_response_string(self, response: str) -> str:',
        '        """',
        '        深度清理SDK响应中的各种前缀和标记',
        '',
        '        Args:',
        '            response: SDK原始响应字符串',
        '',
        '        Returns:',
        '            清理后的字符串，包含核心状态信息',
        '',
        '        示例:',
        '            "[SUCCESS] Ready for Review" → "Ready for Review"',
        '            "Success: Ready for Review" → "Ready for Review"',
        '            "Status: **Ready for Review**" → "Ready for Review"',
        '        """',
        '        if not response:',
        '            return ""',
        '',
        '        cleaned = response.strip()',
        '',
        '        # 步骤1: 处理多层级冒号',
        '        # 输入: "Status: Analysis Result: Ready for Review"',
        '        # 输出: "Ready for Review"',
        '        while ":" in cleaned:',
        '            parts = cleaned.split(":", 1)',
        '            if len(parts) == 2 and parts[1].strip():',
        '                # 检查后半部分是否包含有效内容',
        '                second_part = parts[1].strip()',
        '                if len(second_part) > 2:  # 至少3个字符（避免": x"这类）',
        '                    cleaned = second_part',
        '                else:',
        '                    break',
        '            else:',
        '                break',
        '',
        '        # 步骤2: 移除方括号标记',
        '        # [SUCCESS], [ERROR], [Thinking] 等',
        '        import re',
        '        cleaned = re.sub(r\'^\\[[^\\]]+\\]\\s*\', \'\', cleaned)',
        '',
        '        # 步骤3: 移除冒号前缀',
        '        # Success:, Error:, Result: 等',
        '        cleaned = re.sub(r\'^\\w+:\\s*\', \'\', cleaned)',
        '',
        '        # 步骤4: 移除其他标记',
        '        cleaned = cleaned.replace("[Thinking]", "")',
        '        cleaned = cleaned.replace("[Tool result]", "")',
        '        cleaned = cleaned.replace("**", "")  # 粗体',
        '        cleaned = cleaned.replace("*", "")   # 斜体',
        '        cleaned = cleaned.replace("`", "")   # 代码标记',
        '',
        '        # 步骤5: 最终清理',
        '        cleaned = cleaned.strip()',
        '',
        '        # 记录清理过程（用于调试）',
        '        logger.debug(',
        '            f"Response cleaning: \'{response[:50]}...\' → \'{cleaned}\'"',
        '        )',
        '',
        '        return cleaned',
        '',
        '    def _extract_status_from_response(self, response: str) -> str:',
        '        """',
        '        从AI响应中提取状态值 - 重构版本',
        '',
        '        重构要点:',
        '        1. 利用成熟的 _normalize_story_status 逻辑',
        '        2. 确保只返回7种标准状态之一',
        '        3. 增强错误处理和日志记录',
        '',
        '        Args:',
        '            response: AI响应字符串',
        '',
        '        Returns:',
        '            标准状态字符串 (7种之一)，或 "unknown" 如果解析失败',
        '        """',
        '        # 步骤1: 输入验证',
        '        if not response:',
        '            logger.warning("SimpleStatusParser: Received empty response from AI")',
        '            return "unknown"',
        '',
        '        # 步骤2: 深度清理响应',
        '        cleaned = self._clean_response_string(response)',
        '',
        '        # 步骤3: 验证清理结果',
        '        if not cleaned:',
        '            logger.warning(',
        '                f"SimpleStatusParser: Response became empty after cleaning: \'{response[:50]}...\'"',
        '            )',
        '            return "unknown"',
        '',
        '        # 步骤4: 委托给 _normalize_story_status 进行标准化',
        '        try:',
        '            # 执行标准化',
        '            normalized = _normalize_story_status(cleaned)',
        '',
        '            # 步骤5: 验证结果',
        '            if normalized in CORE_STATUS_VALUES:',
        '                logger.debug(',
        '                    f"Status extraction: \'{response[:50]}...\' → \'{cleaned}\' → \'{normalized}\'"',
        '                )',
        '                return normalized',
        '            else:',
        '                logger.warning(',
        '                    f"SimpleStatusParser: Normalization returned invalid status \'{normalized}\' "',
        '                    f"from input \'{response[:50]}...\'"',
        '                )',
        '                return "unknown"',
        '',
        '        except ImportError as e:',
        '            logger.error(',
        '                f"SimpleStatusParser: Cannot import _normalize_story_status: {e}"',
        '            )',
        '            # 回退到内置的简单匹配',
        '            return self._simple_fallback_match(cleaned)',
        '        except Exception as e:',
        '            logger.error(',
        '                f"SimpleStatusParser: Unexpected error during normalization: {e}",',
        '                exc_info=True',
        '            )',
        '            return "unknown"',
        '',
        '    def _simple_fallback_match(self, cleaned: str) -> str:',
        '        """',
        '        简单的状态匹配回退方案',
        '',
        '        当无法使用 _normalize_story_status 时，使用内置的简单匹配逻辑',
        '        仅支持基本的关键词匹配，不处理复杂变体',
        '',
        '        Args:',
        '            cleaned: 清理后的响应字符串',
        '',
        '        Returns:',
        '            标准状态字符串或 "unknown"',
        '        """',
        '        cleaned_lower = cleaned.lower().strip()',
        '',
        '        # 定义基本关键词匹配',
        '        status_patterns = {',
        '            "Draft": ["draft", "草稿"],',
        '            "Ready for Development": ["ready for development", "development", "准备开发"],',
        '            "In Progress": ["in progress", "progress", "进行", "进行中"],',
        '            "Ready for Review": ["ready for review", "review", "审查", "准备审查"],',
        '            "Ready for Done": ["ready for done", "done", "完成", "准备完成"],',
        '            "Done": ["done", "completed", "complete", "已完成"],',
        '            "Failed": ["failed", "fail", "failure", "失败"]',
        '        }',
        '',
        '        # 遍历匹配',
        '        for status, keywords in status_patterns.items():',
        '            for keyword in keywords:',
        '                if keyword in cleaned_lower:',
        '                    logger.debug(',
        '                        f"Fallback match: \'{cleaned}\' → \'{status}\' (via \'{keyword}\')"',
        '                    )',
        '                    return status',
        '',
        '        # 无匹配',
        '        logger.warning(',
        '            f"SimpleStatusParser: No fallback match for status: \'{cleaned}\'"',
        '        )',
        '        return "unknown"',
    ]

    new_lines.extend(methods_to_add)
    new_lines.extend(after_methods)

    # 写入文件
    with open('autoBMAD/epic_automation/story_parser.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print("Fixed story_parser.py class structure - v5")
    print(f"Added methods: {len(methods_to_add)} lines")

if __name__ == '__main__':
    fix_story_parser()
