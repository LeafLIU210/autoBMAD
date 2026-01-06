import re

# Read the file
with open(r'D:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py', 'r') as f:
    content = f.read()

# Find and replace the problematic import section
pattern = r'# Type aliases for SDK classes.*?# Import Claude SDK types for proper type checking'
replacement = '''# Type aliases for SDK classes
try:
    from claude_agent_sdk import query, ResultMessage
    _query = query
    _ResultMessage = ResultMessage
    _sdk_available = True  # type: ignore
except ImportError:
    _query = None  # type: ignore
    _ResultMessage = None  # type: ignore  # type: ignore
    _sdk_available = False  # type: ignore

# Re-export with proper types
query = _query
ResultMessage = _ResultMessage

# Import Claude SDK types for proper type checking'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open(r'D:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py', 'w') as f:
    f.write(content)

print("Fixed sdk_wrapper.py!")
