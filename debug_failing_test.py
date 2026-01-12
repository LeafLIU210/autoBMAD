import sys
sys.path.insert(0, '/d/GITHUB/pytQt_template')

from autoBMAD.spec_automation.spec_generator import SpecGenerator
from autoBMAD.spec_automation.spec_parser import SpecParser

generator = SpecGenerator()
parser = SpecParser()

# Test a normal spec
spec_content = """# Name
## Version
1.0.0
## Description
This is a description
## Requirements
- Req 1
"""

print("Testing normal spec parsing:")
print(spec_content)
print("="*50)
parsed = parser.parse(spec_content)
print(f"Parsed name: {repr(parsed.name)}")
print(f"Parsed version: {repr(parsed.version)}")
print(f"Parsed description: {repr(parsed.description)}")
