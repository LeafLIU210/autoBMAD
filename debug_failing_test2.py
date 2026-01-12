import sys
sys.path.insert(0, '/d/GITHUB/pytQt_template')

from autoBMAD.spec_automation.spec_generator import SpecGenerator
from autoBMAD.spec_automation.spec_parser import SpecParser

# Patch the parser to add debug output
original_parse_markdown = SpecParser._parse_markdown

def debug_parse_markdown(self, content):
    print("=== DEBUG PARSE ===")
    lines = content.split("\n")
    for i, line in enumerate(lines):
        print(f"Line {i}: {repr(line)}")
    print("===================")
    return original_parse_markdown(self, content)

SpecParser._parse_markdown = debug_parse_markdown

parser = SpecParser()

# Test a normal spec
spec_content = """# Name
## Version
1.0.0
"""

print("Testing normal spec parsing:")
parsed = parser.parse(spec_content)
print(f"\nParsed name: {repr(parsed.name)}")
print(f"Parsed version: {repr(parsed.version)}")
