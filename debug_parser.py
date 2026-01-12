import sys
sys.path.insert(0, '/d/GITHUB/pytQt_template')

from autoBMAD.spec_automation.spec_generator import SpecGenerator
from autoBMAD.spec_automation.spec_parser import SpecParser

generator = SpecGenerator()
parser = SpecParser()

# Simulate the failing case
spec = generator.generate(
    name="0",
    version="0",
    description="## 0",
    requirements=[]
)

markdown = generator.to_markdown(spec)
print("Generated Markdown:")
print(markdown)
print("\n" + "="*50 + "\n")

parsed = parser.parse(markdown)
print("Parsed Description:")
print(repr(parsed.description))
print("\nExpected Description:")
print(repr(spec.description))
