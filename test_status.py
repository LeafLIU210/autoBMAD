#!/usr/bin/env python
import re

# Read story file
story_path = r'D:\GITHUB\pytQt_template\docs\stories\004.1.specdriver-core-orchestrator.md'

with open(story_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Test non-escaped pattern
pattern = r'## Status\n**Status**:\s*\*(.*?)\*'

print("Testing non-escaped pattern:")
print(f"Pattern: {pattern!r}")
print()

match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
if match:
    print(f"SUCCESS: {match.group(1).strip()!r}")
else:
    print("FAILED")

