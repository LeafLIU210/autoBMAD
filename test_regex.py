#!/usr/bin/env python
import re

# Read the file
with open('/d/GITHUB/pytQt_template/docs/stories/004.1.specdriver-core-orchestrator.md', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== File content (first 500 chars) ===")
print(repr(content[:500]))
print()

# Test pattern
pattern = r'## Status\s*[\r\n]+\s*\*\*Status\*\*:\s*\*\*([^*]+)\*\*'
print(f"=== Testing pattern: {pattern} ===")
match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)

if match:
    print(f"✓ Status found: '{match.group(1).strip()}'")
else:
    print("✗ No match found")
    # Try to find ## Status
    if '## Status' in content:
        print('Found "## Status" in file')
        idx = content.find('## Status')
        print('Context around "## Status":', repr(content[idx:idx+100]))
