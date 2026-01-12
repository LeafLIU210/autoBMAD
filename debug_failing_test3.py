import sys
sys.path.insert(0, '/d/GITHUB/pytQt_template')

from autoBMAD.spec_automation.spec_parser import SpecParser

# Patch the parser to add debug output
original_parse = SpecParser.parse

def debug_parse(self, content):
    print(f"Parsing content:\n{content}\n")
    result = original_parse(self, content)
    print(f"Result: name={repr(result.name)}, version={repr(result.version)}")
    return result

SpecParser.parse = debug_parse

parser = SpecParser()

# Test a normal spec
spec_content = """# Name
## Version
1.0.0
"""

print("Testing normal spec parsing:")
parsed = parser.parse(spec_content)
print(f"\nFinal parsed name: {repr(parsed.name)}")
print(f"Final parsed version: {repr(parsed.version)}")
