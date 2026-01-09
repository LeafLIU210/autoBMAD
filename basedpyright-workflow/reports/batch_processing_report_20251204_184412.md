# BasedPyright 批量处理报告

**生成时间**: 2025-12-04 18:44:12
**源文件**: `basedpyright_errors_only_20251204_183815.json`

## 执行摘要

- **原始错误数量**: 389
- **去重后错误数量**: 370
- **处理耗时**: 0.06秒
- **错误分组数量**: 22
- **可自动修复错误**: 0

## 错误分类统计

| 分类 | 数量 | 占比 |
|------|------|------|
| simple | 0 | 0.0% |
| complex | 0 | 0.0% |
| manual | 370 | 100.0% |

## 严重程度统计

| 严重程度 | 数量 | 占比 |
|----------|------|------|
| low | 0 | 0.0% |
| medium | 370 | 100.0% |
| high | 0 | 0.0% |
| critical | 0 | 0.0% |

## Top 10 错误文件

| 文件路径 | 错误数量 |
|----------|----------|
| `d:\Python\bilibiliup\src\output\business_intelligence_generator.py` | 66 |
| `d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py` | 43 |
| `d:\Python\bilibiliup\src\cli\commands\audio.py` | 32 |
| `d:\Python\bilibiliup\src\output\business_intelligence.py` | 28 |
| `d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py` | 25 |
| `d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py` | 20 |
| `d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py` | 20 |
| `d:\Python\bilibiliup\src\audio\downloader\batch_processor.py` | 19 |
| `d:\Python\bilibiliup\src\audio\storage\audio_manager.py` | 17 |
| `d:\Python\bilibiliup\src\ai\speech\service.py` | 14 |

## 错误分组分析

### 分组 1: reportMissingTypeArgument:"<value>" 泛型类应有类型参数 (reportMissingTypeArgument)...

- **错误数量**: 41
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:114**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

2. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:834**
   - **错误**: "List" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

3. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:95**
   - **错误**: "Future" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

4. **d:\Python\bilibiliup\src\audio\downloader\file_manager.py:85**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

5. **d:\Python\bilibiliup\src\audio\downloader\file_manager.py:226**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

6. **d:\Python\bilibiliup\src\audio\downloader\file_manager.py:365**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

7. **d:\Python\bilibiliup\src\audio\downloader\file_manager.py:426**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

8. **d:\Python\bilibiliup\src\audio\jijidown_client\connection_manager.py:321**
   - **错误**: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

9. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:99**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

10. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:147**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

11. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:210**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

12. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:347**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

13. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:412**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

14. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:507**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

15. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:129**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

16. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:179**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

17. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:202**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

18. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:222**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

19. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:254**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

20. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:279**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

21. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:311**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

22. **d:\Python\bilibiliup\src\audio\jijidown_client\proto_utils.py:349**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

23. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:184**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

24. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:226**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

25. **d:\Python\bilibiliup\src\audio\storage\storage_config.py:29**
   - **错误**: "list" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

26. **d:\Python\bilibiliup\src\audio\storage\storage_config.py:48**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

27. **d:\Python\bilibiliup\src\audio\storage\storage_config.py:72**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

28. **d:\Python\bilibiliup\src\cli\commands\audio.py:310**
   - **错误**: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

29. **d:\Python\bilibiliup\src\cli\commands\audio.py:355**
   - **错误**: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

30. **d:\Python\bilibiliup\src\cli\commands\audio.py:730**
   - **错误**: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

31. **d:\Python\bilibiliup\src\cli\commands\audio.py:1098**
   - **错误**: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

32. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:889**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

33. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:899**
   - **错误**: "List" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

34. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:909**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

35. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:924**
   - **错误**: "Tuple" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

36. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:941**
   - **错误**: "Tuple" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

37. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:957**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

38. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:972**
   - **错误**: "Dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

39. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:987**
   - **错误**: "Tuple" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

40. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:1007**
   - **错误**: "Tuple" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

41. **d:\Python\bilibiliup\src\scraping\video_scraper.py:2016**
   - **错误**: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
   - **规则**: reportMissingTypeArgument
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

---

### 分组 2: unknown:"<value>" 类型的实参无法赋值给函数 "<value>" 中 "<value>" 类型的形参...

- **错误数量**: 144
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:134**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:217**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:218**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:219**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:220**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:350**
   - **错误**: "Column[int] | Literal[0]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

7. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:736**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

8. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:336**
   - **错误**: "Column[Unknown]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToFloat" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

9. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:470**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

10. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:471**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

11. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:472**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

12. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:473**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

13. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:474**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

14. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:478**
   - **错误**: "Column[Unknown]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToFloat" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

15. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:531**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

16. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:532**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

17. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:533**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

18. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:534**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

19. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:535**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToInt" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

20. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:736**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "len" 中 "Sized" 类型的形参 "obj"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

21. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:1002**
   - **错误**: "dict[str, str | Dict[str, Any] | dict[str, Any | str | float | Dict[str, int] | List[str] | None] | None]" 类型的实参无法赋值给函数 "__setitem__" 中 "str | datetime | None" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

22. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:1094**
   - **错误**: "dict[str, int]" 类型的实参无法赋值给函数 "__setitem__" 中 "int | float" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

23. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:1255**
   - **错误**: "Column[Unknown] | float" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToFloat" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

24. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:1258**
   - **错误**: "Column[Unknown] | float" 类型的实参无法赋值给函数 "__new__" 中 "ConvertibleToFloat" 类型的形参 "x"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

25. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str | None" 类型的形参 "language"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

26. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str" 类型的形参 "task"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

27. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "bool" 类型的形参 "log_progress"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

28. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "int" 类型的形参 "beam_size"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

29. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "int" 类型的形参 "best_of"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

30. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float" 类型的形参 "patience"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

31. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float" 类型的形参 "length_penalty"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

32. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float" 类型的形参 "repetition_penalty"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

33. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "int" 类型的形参 "no_repeat_ngram_size"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

34. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float | List[float] | Tuple[float, ...]" 类型的形参 "temperature"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

35. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float | None" 类型的形参 "compression_ratio_threshold"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

36. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float | None" 类型的形参 "log_prob_threshold"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

37. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float | None" 类型的形参 "no_speech_threshold"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

38. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "bool" 类型的形参 "condition_on_previous_text"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

39. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float" 类型的形参 "prompt_reset_on_temperature"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

40. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str | Iterable[int] | None" 类型的形参 "initial_prompt"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

41. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str | None" 类型的形参 "prefix"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

42. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "bool" 类型的形参 "suppress_blank"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

43. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "List[int] | None" 类型的形参 "suppress_tokens"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

44. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "bool" 类型的形参 "without_timestamps"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

45. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float" 类型的形参 "max_initial_timestamp"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

46. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "bool" 类型的形参 "word_timestamps"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

47. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str" 类型的形参 "prepend_punctuations"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

48. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str" 类型的形参 "append_punctuations"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

49. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "bool" 类型的形参 "multilingual"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

50. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "bool" 类型的形参 "vad_filter"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

51. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "dict[Unknown, Unknown] | VadOptions | None" 类型的形参 "vad_parameters"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

52. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "int | None" 类型的形参 "max_new_tokens"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

53. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "int | None" 类型的形参 "chunk_length"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

54. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str | List[float]" 类型的形参 "clip_timestamps"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

55. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float | None" 类型的形参 "hallucination_silence_threshold"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

56. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "str | None" 类型的形参 "hotwords"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

57. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "float | None" 类型的形参 "language_detection_threshold"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

58. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:196**
   - **错误**: "str | int | float | Unknown | bool" 类型的实参无法赋值给函数 "transcribe" 中 "int" 类型的形参 "language_detection_segments"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

59. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:365**
   - **错误**: "str" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | None" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

60. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:372**
   - **错误**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | None" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

61. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:377**
   - **错误**: "str" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | None" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

62. **d:\Python\bilibiliup\src\ai\speech\service.py:207**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__new__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

63. **d:\Python\bilibiliup\src\ai\speech\service.py:207**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

64. **d:\Python\bilibiliup\src\ai\speech\service.py:208**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "file_path"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

65. **d:\Python\bilibiliup\src\ai\speech\service.py:213**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "transcribe_audio_file" 中 "str" 类型的形参 "audio_path"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

66. **d:\Python\bilibiliup\src\ai\speech\service.py:214**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "transcribe_audio_file" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

67. **d:\Python\bilibiliup\src\ai\speech\service.py:478**
   - **错误**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | None" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

68. **d:\Python\bilibiliup\src\ai\speech\service.py:483**
   - **错误**: "str" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | None" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

69. **d:\Python\bilibiliup\src\audio\AudioDownloadManager.py:262**
   - **错误**: "dict[str, Column[int] | Column[str]]" 类型的实参无法赋值给函数 "__setitem__" 中 "str" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

70. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:152**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

71. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:369**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "_simulate_download_progress" 中 "int" 类型的形参 "audio_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

72. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:536**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "get_by_video_id" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

73. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:245**
   - **错误**: "float | None" 类型的实参无法赋值给函数 "update_task_progress" 中 "float" 类型的形参 "progress_percent"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

74. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:95**
   - **错误**: "int" 类型的实参无法赋值给函数 "__setitem__" 中 "str" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

75. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:97**
   - **错误**: "int" 类型的实参无法赋值给函数 "__setitem__" 中 "str" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

76. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:130**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__new__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

77. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:130**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

78. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:136**
   - **错误**: "Column[int]" 类型的实参无法赋值给函数 "update_audio_status" 中 "int" 类型的形参 "audio_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

79. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:137**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "update_audio_status" 中 "str" 类型的形参 "status"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

80. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:167**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__new__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

81. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:167**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

82. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:200**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__new__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

83. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:200**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "StrPath" 类型的形参 "args"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

84. **d:\Python\bilibiliup\src\cli\commands\export.py:706**
   - **错误**: "type[ReportFormat]" 类型的实参无法赋值给函数 "export_report" 中 "str" 类型的形参 "format"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

85. **d:\Python\bilibiliup\src\config\settings.py:211**
   - **错误**: "Path" 类型的实参无法赋值给函数 "append" 中 "str" 类型的形参 "object"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

86. **d:\Python\bilibiliup\src\output\business_intelligence.py:335**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "get_by_video_id" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

87. **d:\Python\bilibiliup\src\output\business_intelligence.py:340**
   - **错误**: "dict[str, Column[str] | Column[Unknown] | int]" 类型的实参无法赋值给函数 "__setitem__" 中 "Column[str] | Column[datetime] | Column[int] | float" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

88. **d:\Python\bilibiliup\src\output\business_intelligence.py:350**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "analyze_patterns" 中 "str" 类型的形参 "transcript"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

89. **d:\Python\bilibiliup\src\output\business_intelligence.py:352**
   - **错误**: "dict[str, float | List[str] | None]" 类型的实参无法赋值给函数 "__setitem__" 中 "Column[str] | Column[datetime] | Column[int] | float" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

90. **d:\Python\bilibiliup\src\output\business_intelligence.py:365**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "analyze_video_with_speech" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

91. **d:\Python\bilibiliup\src\output\business_intelligence.py:369**
   - **错误**: "dict[str, ContentStructureMetrics | SuccessPatternMetrics | Dict[str, Any] | dict[str, float | Dict[str, int]] | None]" 类型的实参无法赋值给函数 "__setitem__" 中 "Column[str] | Column[datetime] | Column[int] | float" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

92. **d:\Python\bilibiliup\src\output\business_intelligence.py:382**
   - **错误**: "None" 类型的实参无法赋值给函数 "__setitem__" 中 "Column[str] | Column[datetime] | Column[int] | float" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

93. **d:\Python\bilibiliup\src\output\business_intelligence.py:393**
   - **错误**: "dict[str, List[str]]" 类型的实参无法赋值给函数 "__setitem__" 中 "Column[str] | Column[datetime] | Column[int] | float" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

94. **d:\Python\bilibiliup\src\output\business_intelligence.py:401**
   - **错误**: "None" 类型的实参无法赋值给函数 "__setitem__" 中 "Column[str] | Column[datetime] | Column[int] | float" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

95. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:229**
   - **错误**: "ReportConfiguration | None" 类型的实参无法赋值给函数 "_create_error_report" 中 "ReportConfiguration" 类型的形参 "config"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

96. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:375**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "analyze_patterns" 中 "str" 类型的形参 "transcript"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

97. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:397**
   - **错误**: "Literal['high_performing_videos']" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

98. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:399**
   - **错误**: "Dict[str, int]" 类型的实参无法赋值给函数 "__setitem__" 中 "dict[str, int | list[Unknown] | dict[Unknown, Unknown]] | list[Unknown]" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

99. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:434**
   - **错误**: "Dict[str, Any] | None" 类型的实参无法赋值给函数 "generate_business_intelligence" 中 "ContentStructureMetrics" 类型的形参 "content_structure"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

100. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:435**
   - **错误**: "List[str] | None" 类型的实参无法赋值给函数 "generate_business_intelligence" 中 "SuccessPatternMetrics" 类型的形参 "success_patterns"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

101. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:435**
   - **错误**: "Dict[str, Any] | None" 类型的实参无法赋值给函数 "generate_business_intelligence" 中 "ContentInsights" 类型的形参 "content_insights"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

102. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:464**
   - **错误**: "Literal['total_insights']" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

103. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:465**
   - **错误**: "Literal['high_priority_insights']" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

104. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:466**
   - **错误**: "Literal['insight_categories']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

105. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:467**
   - **错误**: "dict[str, int | dict[Unknown, Unknown]] | list[Unknown]" 类型的实参无法赋值给函数 "_aggregate_optimization_roadmap" 中 "List[Dict[Unknown, Unknown]]" 类型的形参 "strategic_insights"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

106. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:506**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "_recommend_content_frameworks" 中 "str" 类型的形参 "content_text"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

107. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:506**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "_recommend_content_frameworks" 中 "str" 类型的形参 "title"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

108. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:507**
   - **错误**: "Dict[str, Any] | None" 类型的实参无法赋值给函数 "_recommend_content_frameworks" 中 "ContentStructureMetrics" 类型的形参 "content_structure"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

109. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:507**
   - **错误**: "List[str] | None" 类型的实参无法赋值给函数 "_recommend_content_frameworks" 中 "SuccessPatternMetrics" 类型的形参 "success_patterns"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

110. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:535**
   - **错误**: "Literal['recommended_frameworks']" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

111. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:536**
   - **错误**: "Literal['framework_distribution']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

112. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:537**
   - **错误**: "dict[str, int | dict[Unknown, Unknown]] | list[Unknown]" 类型的实参无法赋值给函数 "_generate_framework_guidance" 中 "List[Dict[Unknown, Unknown]]" 类型的形参 "recommendations"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

113. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:569**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "_identify_promotion_opportunities" 中 "str" 类型的形参 "content_text"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

114. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:569**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "_identify_promotion_opportunities" 中 "str" 类型的形参 "title"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

115. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:569**
   - **错误**: "Dict[str, Any] | None" 类型的实参无法赋值给函数 "_identify_promotion_opportunities" 中 "ContentStructureMetrics" 类型的形参 "content_structure"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

116. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:627**
   - **错误**: "Literal['total_opportunities']" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

117. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:628**
   - **错误**: "Literal['high_value_opportunities']" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

118. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:629**
   - **错误**: "Literal['opportunity_types']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

119. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:630**
   - **错误**: "dict[str, int | dict[Unknown, Unknown]] | list[Unknown]" 类型的实参无法赋值给函数 "_generate_promotion_roadmap" 中 "List[Dict[Unknown, Unknown]]" 类型的形参 "opportunities"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

120. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:670**
   - **错误**: "Dict[str, Any] | None" 类型的实参无法赋值给函数 "_calculate_success_improvement_potential" 中 "ContentStructureMetrics" 类型的形参 "content_structure"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

121. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:671**
   - **错误**: "List[str] | None" 类型的实参无法赋值给函数 "_calculate_success_improvement_potential" 中 "SuccessPatternMetrics" 类型的形参 "success_patterns"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

122. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:679**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "_identify_promotion_opportunities" 中 "str" 类型的形参 "content_text"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

123. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:679**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "_identify_promotion_opportunities" 中 "str" 类型的形参 "title"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

124. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:679**
   - **错误**: "Dict[str, Any] | None" 类型的实参无法赋值给函数 "_identify_promotion_opportunities" 中 "ContentStructureMetrics" 类型的形参 "content_structure"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

125. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:728**
   - **错误**: "dict[str, float | int | list[Unknown]]" 类型的实参无法赋值给函数 "__setitem__" 中 "dict[str, float | str]" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

126. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:749**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "len" 中 "Sized" 类型的形参 "obj"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

127. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:777**
   - **错误**: "Column[str]" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "video_id"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

128. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:780**
   - **错误**: "MockContentStructure" 类型的实参无法赋值给函数 "__init__" 中 "Dict[str, Any] | None" 类型的形参 "content_structure"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

129. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:781**
   - **错误**: "MockSuccessPatterns" 类型的实参无法赋值给函数 "__init__" 中 "List[str] | None" 类型的形参 "success_patterns"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

130. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:782**
   - **错误**: "MockEnhancedInsights" 类型的实参无法赋值给函数 "__init__" 中 "Dict[str, Any] | None" 类型的形参 "enhanced_insights"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

131. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:783**
   - **错误**: "Column[str] | Literal['']" 类型的实参无法赋值给函数 "__init__" 中 "str | None" 类型的形参 "transcript_full_text"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

132. **d:\Python\bilibiliup\src\scraping\content_extractor.py:1045**
   - **错误**: "str | None" 类型的实参无法赋值给函数 "_parse_publish_date" 中 "str" 类型的形参 "text"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

133. **d:\Python\bilibiliup\src\storage\migrations\migration_251201_add_interaction_metrics.py:32**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

134. **d:\Python\bilibiliup\src\storage\migrations\migration_251201_add_interaction_metrics.py:112**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

135. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:33**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

136. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:185**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

137. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:32**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

138. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:100**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

139. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:214**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

140. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:254**
   - **错误**: "Engine | None" 类型的实参无法赋值给函数 "reflect" 中 "Connection" 类型的形参 "bind"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

141. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:153**
   - **错误**: "int" 类型的实参无法赋值给函数 "__setitem__" 中 "str | dict[Unknown, Unknown]" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

142. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:439**
   - **错误**: "int" 类型的实参无法赋值给函数 "__setitem__" 中 "str | dict[Unknown, Unknown]" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

143. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:488**
   - **错误**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "str | dict[Unknown, Unknown]" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

144. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:503**
   - **错误**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "str | dict[Unknown, Unknown]" 类型的形参 "value"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 3: unknown:ColumnElement[bool] 类型的条件值无效...

- **错误数量**: 6
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:211**
   - **错误**: ColumnElement[bool] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:315**
   - **错误**: ColumnElement[bool] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:694**
   - **错误**: ColumnElement[bool] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\output\business_intelligence.py:285**
   - **错误**: ColumnElement[bool] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\output\business_intelligence.py:304**
   - **错误**: ColumnElement[bool] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:389**
   - **错误**: ColumnElement[bool] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 4: unknown:Column[int] | <subclass of Column[int] and int> | ...

- **错误数量**: 4
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:231**
   - **错误**: Column[int] | <subclass of Column[int] and int> | <subclass of Column[int] and float> | Literal[False] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:232**
   - **错误**: Column[int] | <subclass of Column[int] and int> | <subclass of Column[int] and float> | Literal[False] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:233**
   - **错误**: Column[int] | <subclass of Column[int] and int> | <subclass of Column[int] and float> | Literal[False] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:234**
   - **错误**: Column[int] | <subclass of Column[int] and int> | <subclass of Column[int] and float> | Literal[False] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 5: unknown:"<value>" 类型不匹配返回类型 "<value>"...

- **错误数量**: 6
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:262**
   - **错误**: "float | ColumnElement[_NUMERIC]" 类型不匹配返回类型 "float"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\analysis\content_intelligence.py:429**
   - **错误**: "TrendResult | None" 类型不匹配返回类型 "Dict[str, Any]"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\audio\AudioDownloadManager.py:271**
   - **错误**: "dict[str, str]" 类型不匹配返回类型 "Dict[str, str | Dict[str, str | int | None]]"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\audio\jijidown_client\connection_manager.py:244**
   - **错误**: "Channel" 类型不匹配返回类型 "Channel"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\output\business_intelligence.py:302**
   - **错误**: "Column[Unknown]" 类型不匹配返回类型 "float"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\output\business_intelligence.py:314**
   - **错误**: "ColumnElement[_NUMERIC]" 类型不匹配返回类型 "float"
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 6: unknown:SpeechTranscription | Column[str] | None 类型的条件值无效...

- **错误数量**: 2
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:333**
   - **错误**: SpeechTranscription | Column[str] | None 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:374**
   - **错误**: SpeechTranscription | Column[str] | None 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 7: unknown:Column[str] 类型的条件值无效...

- **错误数量**: 5
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:335**
   - **错误**: Column[str] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:740**
   - **错误**: Column[str] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:1672**
   - **错误**: Column[str] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:1673**
   - **错误**: Column[str] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\output\business_intelligence.py:336**
   - **错误**: Column[str] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 8: unknown:Column[str] | bool 类型的条件值无效...

- **错误数量**: 2
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:466**
   - **错误**: Column[str] | bool 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:467**
   - **错误**: Column[str] | bool 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 9: unknown:无法为 "<value>" 类的 "<value>" 属性赋值...

- **错误数量**: 2
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\analysis\enhanced_analyzer.py:731**
   - **错误**: 无法为 "EnhancedSpeechAnalysisResult" 类的 "transcript_text" 属性赋值
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\audio\jijidown_client\connection_manager.py:237**
   - **错误**: 无法为 "ConnectionManager*" 类的 "_channel" 属性赋值
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 10: unknown:无法访问 "<value>" 类的 "<value>" 属性...

- **错误数量**: 45
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:33**
   - **错误**: 无法访问 "ASRModelConfig" 类的 "dict" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:184**
   - **错误**: 无法访问 "ASRModelConfig" 类的 "logprob_threshold" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:338**
   - **错误**: 无法访问 "ASRModelConfig" 类的 "dict" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:373**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "total_duration" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:374**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "word_count" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\ai\speech\service.py:149**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "language_detected" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

7. **d:\Python\bilibiliup\src\ai\speech\service.py:427**
   - **错误**: 无法访问 "ASRModelConfig" 类的 "dict" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

8. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:460**
   - **错误**: 无法访问 "AudioRepository" 类的 "get_db_session_safe" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

9. **d:\Python\bilibiliup\src\cli\commands\audio.py:227**
   - **错误**: 无法访问 "JijidownGrpcClient" 类的 "connect" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

10. **d:\Python\bilibiliup\src\cli\commands\audio.py:285**
   - **错误**: 无法访问 "JijidownGrpcClient" 类的 "connect" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

11. **d:\Python\bilibiliup\src\cli\commands\audio.py:539**
   - **错误**: 无法访问 "TranscriptionRepository" 类的 "exists_for_audio" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

12. **d:\Python\bilibiliup\src\cli\commands\audio.py:544**
   - **错误**: 无法访问 "AudioRepository" 类的 "get_files_for_transcription" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

13. **d:\Python\bilibiliup\src\cli\commands\audio.py:681**
   - **错误**: 无法访问 "TranscriptionRepository" 类的 "exists_for_audio" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

14. **d:\Python\bilibiliup\src\cli\commands\audio.py:685**
   - **错误**: 无法访问 "AudioRepository" 类的 "get_files_for_transcription" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

15. **d:\Python\bilibiliup\src\cli\commands\audio.py:770**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "text" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

16. **d:\Python\bilibiliup\src\cli\commands\audio.py:772**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "language_detected" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

17. **d:\Python\bilibiliup\src\cli\commands\audio.py:774**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "text" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

18. **d:\Python\bilibiliup\src\cli\commands\audio.py:785**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "language_detected" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

19. **d:\Python\bilibiliup\src\cli\commands\audio.py:786**
   - **错误**: 无法访问 "TranscriptionResult" 类的 "text" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

20. **d:\Python\bilibiliup\src\cli\commands\audio.py:923**
   - **错误**: 无法访问 "TranscriptionRepository" 类的 "get_for_analysis" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

21. **d:\Python\bilibiliup\src\cli\commands\audio.py:1048**
   - **错误**: 无法访问 "TranscriptionRepository" 类的 "get_for_analysis" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

22. **d:\Python\bilibiliup\src\cli\commands\audio.py:1245**
   - **错误**: 无法访问 "dict[str, str | int]" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

23. **d:\Python\bilibiliup\src\cli\commands\audio.py:1459**
   - **错误**: 无法访问 "AudioRepository" 类的 "get_recent_completed" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

24. **d:\Python\bilibiliup\src\cli\commands\audio.py:1469**
   - **错误**: 无法访问 "TranscriptionRepository" 类的 "get_recent_completed" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

25. **d:\Python\bilibiliup\src\cli\commands\audio.py:1481**
   - **错误**: 无法访问 "AudioRepository" 类的 "get_total_storage_size" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

26. **d:\Python\bilibiliup\src\cli\commands\audio.py:1493**
   - **错误**: 无法访问 "JijidownGrpcClient" 类的 "health_check" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

27. **d:\Python\bilibiliup\src\cli\commands\export.py:715**
   - **错误**: 无法访问 "BusinessIntelligenceGenerator" 类的 "get_generation_statistics" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

28. **d:\Python\bilibiliup\src\output\business_intelligence.py:213**
   - **错误**: 无法访问 "VideoRepository" 类的 "get_by_ids" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

29. **d:\Python\bilibiliup\src\output\business_intelligence.py:662**
   - **错误**: 无法访问 "int" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

30. **d:\Python\bilibiliup\src\output\business_intelligence.py:664**
   - **错误**: 无法访问 "int" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

31. **d:\Python\bilibiliup\src\output\business_intelligence.py:666**
   - **错误**: 无法访问 "int" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

32. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:379**
   - **错误**: 无法访问 "dict[str, int | list[Unknown] | dict[Unknown, Unknown]]" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

33. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:449**
   - **错误**: 无法访问 "dict[str, int | dict[Unknown, Unknown]]" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

34. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:496**
   - **错误**: 无法访问 "dict[str, int | dict[Unknown, Unknown]]" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

35. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:525**
   - **错误**: 无法访问 "dict[str, int | dict[Unknown, Unknown]]" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

36. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:596**
   - **错误**: 无法访问 "dict[str, int | dict[Unknown, Unknown]]" 类的 "append" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

37. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:605**
   - **错误**: 无法访问 "dict[str, int | dict[Unknown, Unknown]]" 类的 "extend" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

38. **d:\Python\bilibiliup\src\scraping\content_extractor.py:687**
   - **错误**: 无法访问 "Locator" 类的 "query_selector" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

39. **d:\Python\bilibiliup\src\scraping\content_extractor.py:795**
   - **错误**: 无法访问 "Locator" 类的 "query_selector" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

40. **d:\Python\bilibiliup\src\scraping\content_extractor.py:911**
   - **错误**: 无法访问 "Locator" 类的 "query_selector" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

41. **d:\Python\bilibiliup\src\scraping\content_extractor.py:1067**
   - **错误**: 无法访问 "Locator" 类的 "query_selector" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

42. **d:\Python\bilibiliup\src\scraping\content_extractor.py:1076**
   - **错误**: 无法访问 "Locator" 类的 "query_selector_all" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

43. **d:\Python\bilibiliup\src\scraping\video_scraper.py:622**
   - **错误**: 无法访问 "VideoScraper*" 类的 "_extract_text_with_playwright" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

44. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:151**
   - **错误**: 无法访问 "str" 类的 "values" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

45. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:437**
   - **错误**: 无法访问 "str" 类的 "values" 属性
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 11: reportOptionalMemberAccess:`None` 没有 "<value>" 属性 (reportOptionalMemberAccess...

- **错误数量**: 24
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\speech\asr_engine_backup.py:194**
   - **错误**: `None` 没有 "transcribe" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:261**
   - **错误**: `None` 没有 "cancel_task" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:289**
   - **错误**: `None` 没有 "can_start_more_tasks" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:302**
   - **错误**: `None` 没有 "update_task_progress" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:312**
   - **错误**: `None` 没有 "get_active_tasks" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:318**
   - **错误**: `None` 没有 "finalize_batch" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

7. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:340**
   - **错误**: `None` 没有 "cancel_task" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

8. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:344**
   - **错误**: `None` 没有 "update_task_progress" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

9. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:372**
   - **错误**: `None` 没有 "complete_task" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

10. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:382**
   - **错误**: `None` 没有 "update_task_progress" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

11. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:393**
   - **错误**: `None` 没有 "complete_task" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

12. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:450**
   - **错误**: `None` 没有 "update_task_progress" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

13. **d:\Python\bilibiliup\src\scraping\video_scraper.py:1466**
   - **错误**: `None` 没有 "group" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

14. **d:\Python\bilibiliup\src\scraping\video_scraper.py:1471**
   - **错误**: `None` 没有 "group" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

15. **d:\Python\bilibiliup\src\storage\migrations\migration_251201_add_interaction_metrics.py:42**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

16. **d:\Python\bilibiliup\src\storage\migrations\migration_251201_add_interaction_metrics.py:119**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

17. **d:\Python\bilibiliup\src\storage\migrations\migration_251201_add_interaction_metrics.py:159**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

18. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:35**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

19. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:143**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

20. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:147**
   - **错误**: `None` 没有 "get_table_names" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

21. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:189**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

22. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:34**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

23. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:216**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

24. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:258**
   - **错误**: `None` 没有 "connect" 属性 (reportOptionalMemberAccess)
   - **规则**: reportOptionalMemberAccess
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 12: reportCallIssue:需要传入 <num> 个位置参数 (reportCallIssue)...

- **错误数量**: 5
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\speech\service.py:107**
   - **错误**: 需要传入 1 个位置参数 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:495**
   - **错误**: 需要传入 0 个位置参数 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:289**
   - **错误**: 需要传入 0 个位置参数 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:290**
   - **错误**: 需要传入 0 个位置参数 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:291**
   - **错误**: 需要传入 0 个位置参数 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 13: unknown:无法将 "<value>" 类型的表达式赋值给 "<value>" 类型的参数...

- **错误数量**: 15
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\speech\service.py:185**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "bool" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\ai\speech\service.py:248**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "bool" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\ai\speech\service.py:294**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "bool" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\audio\downloader\file_manager.py:426**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "Path" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:170**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "float" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:171**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

7. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:172**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

8. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:173**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

9. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:174**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

10. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:175**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

11. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:233**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

12. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:329**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "int" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

13. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:38**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

14. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:77**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "int" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

15. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:78**
   - **错误**: 无法将 "None" 类型的表达式赋值给 "int" 类型的参数
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 14: reportGeneralTypeIssues:此处应为类而非 "<value>" (reportGeneralTypeIssues)...

- **错误数量**: 4
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\ai\speech\service.py:249**
   - **错误**: 此处应为类而非 "(obj: object, /) -> TypeIs[(...) -> object]" (reportGeneralTypeIssues)
   - **规则**: reportGeneralTypeIssues
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:132**
   - **错误**: 此处应为类而非 "(obj: object, /) -> TypeIs[(...) -> object]" (reportGeneralTypeIssues)
   - **规则**: reportGeneralTypeIssues
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\audio\downloader\progress_tracker.py:356**
   - **错误**: 此处应为类而非 "(obj: object, /) -> TypeIs[(...) -> object]" (reportGeneralTypeIssues)
   - **规则**: reportGeneralTypeIssues
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\scraping\content_extractor.py:1487**
   - **错误**: 此处应为类而非 "(obj: object, /) -> TypeIs[(...) -> object]" (reportGeneralTypeIssues)
   - **规则**: reportGeneralTypeIssues
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 15: reportCallIssue:"<value>" 参数不存在 (reportCallIssue)...

- **错误数量**: 3
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\audio\downloader\batch_processor.py:362**
   - **错误**: "source_type" 参数不存在 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\cli\commands\audio.py:1350**
   - **错误**: "force_reextract" 参数不存在 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\cli\commands\audio.py:1351**
   - **错误**: "threads" 参数不存在 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 16: reportMissingImports:无法解析导入 "<value>" (reportMissingImports)...

- **错误数量**: 2
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:27**
   - **错误**: 无法解析导入 ".proto" (reportMissingImports)
   - **规则**: reportMissingImports
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

2. **d:\Python\bilibiliup\src\cli\main.py:325**
   - **错误**: 无法解析导入 ".commands.business_intelligence" (reportMissingImports)
   - **规则**: reportMissingImports
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 60.0%

---

### 分组 17: reportPossiblyUnboundVariable:"<value>" 可能未绑定 (reportPossiblyUnboundVariable)...

- **错误数量**: 5
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:86**
   - **错误**: "bvideo_pb2_grpc" 可能未绑定 (reportPossiblyUnboundVariable)
   - **规则**: reportPossiblyUnboundVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\audio\jijidown_client\grpc_client.py:87**
   - **错误**: "task_pb2_grpc" 可能未绑定 (reportPossiblyUnboundVariable)
   - **规则**: reportPossiblyUnboundVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\output\business_intelligence.py:397**
   - **错误**: "patterns" 可能未绑定 (reportPossiblyUnboundVariable)
   - **规则**: reportPossiblyUnboundVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\output\business_intelligence.py:669**
   - **错误**: "patterns" 可能未绑定 (reportPossiblyUnboundVariable)
   - **规则**: reportPossiblyUnboundVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\output\business_intelligence.py:670**
   - **错误**: "patterns" 可能未绑定 (reportPossiblyUnboundVariable)
   - **规则**: reportPossiblyUnboundVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 18: unknown:Column[datetime] 类型的条件值无效...

- **错误数量**: 2
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\audio\storage\audio_manager.py:210**
   - **错误**: Column[datetime] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\output\business_intelligence.py:284**
   - **错误**: Column[datetime] 类型的条件值无效
   - **规则**: unknown
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 19: reportUndefinedVariable:"<value>" 未定义 (reportUndefinedVariable)...

- **错误数量**: 7
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\cli\commands\audio.py:587**
   - **错误**: "ThreadPoolExecutor" 未定义 (reportUndefinedVariable)
   - **规则**: reportUndefinedVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\cli\commands\audio.py:600**
   - **错误**: "as_completed" 未定义 (reportUndefinedVariable)
   - **规则**: reportUndefinedVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\cli\commands\audio.py:843**
   - **错误**: "validate_configuration_complete" 未定义 (reportUndefinedVariable)
   - **规则**: reportUndefinedVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\cli\commands\audio.py:895**
   - **错误**: "get_enhanced_content_analyzer" 未定义 (reportUndefinedVariable)
   - **规则**: reportUndefinedVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\cli\commands\audio.py:1033**
   - **错误**: "get_enhanced_content_analyzer" 未定义 (reportUndefinedVariable)
   - **规则**: reportUndefinedVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\cli\commands\audio.py:1330**
   - **错误**: "validate_configuration_complete" 未定义 (reportUndefinedVariable)
   - **规则**: reportUndefinedVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

7. **d:\Python\bilibiliup\src\cli\commands\audio.py:1510**
   - **错误**: "get_enhanced_content_analyzer" 未定义 (reportUndefinedVariable)
   - **规则**: reportUndefinedVariable
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 20: reportIndexIssue:"<value>" 类型上未定义 "<value>" 方法 (reportIndexIssue)...

- **错误数量**: 17
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\output\business_intelligence.py:388**
   - **错误**: "float" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\output\business_intelligence.py:389**
   - **错误**: "float" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\scraping\content_extractor.py:1596**
   - **错误**: "BaseException" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:65**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:84**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:101**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

7. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:142**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

8. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:212**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

9. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:254**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

10. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:295**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

11. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:344**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

12. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:369**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

13. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:398**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

14. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:425**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

15. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:475**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

16. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:476**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

17. **d:\Python\bilibiliup\src\storage\validations\audio_content_validation.py:477**
   - **错误**: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
   - **规则**: reportIndexIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 21: reportOptionalSubscript:`None` 不支持下标访问 (reportOptionalSubscript)...

- **错误数量**: 2
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\output\business_intelligence.py:388**
   - **错误**: `None` 不支持下标访问 (reportOptionalSubscript)
   - **规则**: reportOptionalSubscript
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\output\business_intelligence.py:389**
   - **错误**: `None` 不支持下标访问 (reportOptionalSubscript)
   - **规则**: reportOptionalSubscript
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

### 分组 22: reportCallIssue:"<value>" 的重载与提供的参数不匹配 (reportCallIssue)...

- **错误数量**: 17
- **可自动修复**: 否
- **通用建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计

#### 错误详情

1. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:397**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

2. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:464**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

3. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:465**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

4. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:466**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

5. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:535**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

6. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:536**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

7. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:627**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

8. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:628**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

9. **d:\Python\bilibiliup\src\output\business_intelligence_generator.py:629**
   - **错误**: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

10. **d:\Python\bilibiliup\src\storage\migrations\migration_251201_add_interaction_metrics.py:32**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

11. **d:\Python\bilibiliup\src\storage\migrations\migration_251201_add_interaction_metrics.py:112**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

12. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:33**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

13. **d:\Python\bilibiliup\src\storage\migrations\migration_251203_audio_content_schema.py:185**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

14. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:32**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

15. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:100**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

16. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:214**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

17. **d:\Python\bilibiliup\src\storage\migrations\migration_512030_add_audio_content.py:254**
   - **错误**: "reflect" 的重载与提供的参数不匹配 (reportCallIssue)
   - **规则**: reportCallIssue
   - **严重程度**: medium
   - **修复建议**: 这个错误需要人工审查，建议检查代码逻辑和类型设计
   - **置信度**: 50.0%

---

## 建议和后续步骤

2. **批量处理**: 优先处理错误分组中的类似问题
4. **持续监控**: 定期运行检查以保持代码质量
