import sys
sys.path.insert(0, '/d/GITHUB/pytQt_template')

from autoBMAD.spec_automation.spec_generator import SpecGenerator
from autoBMAD.spec_automation.spec_parser import SpecParser

generator = SpecGenerator()
parser = SpecParser()

# Test case 1: version = "##"
spec1 = generator.generate(
    name="0",
    version="##",
    description="",
    requirements=[]
)

markdown1 = generator.to_markdown(spec1)
print("Test 1 - version='##'")
print("Generated Markdown:")
print(markdown1)
parsed1 = parser.parse(markdown1)
print(f"Parsed version: {repr(parsed1.version)}")
print(f"Expected version: {repr(spec1.version)}")
print()

# Test case 2: description = "## Name"
spec2 = generator.generate(
    name="0",
    version="0",
    description="## Name",
    requirements=[]
)

markdown2 = generator.to_markdown(spec2)
print("Test 2 - description='## Name'")
print("Generated Markdown:")
print(markdown2)
parsed2 = parser.parse(markdown2)
print(f"Parsed description: {repr(parsed2.description)}")
print(f"Expected description: {repr(spec2.description)}")
