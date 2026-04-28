"""修复 Python 文件中的 Unicode emoji"""
import re
import sys
from pathlib import Path

# Emoji pattern
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "]+", 
    flags=re.UNICODE
)

files = [
    "docuswarm_f1_multidoc_validator_debugger.py",
    "docuswarm_f2_update_context_debugger.py",
    "docuswarm_f3_sdk_skills_debugger.py",
    "docuswarm_f4_template_mapping_debugger.py",
    "docuswarm_f5_allowed_keys_debugger.py",
    "docuswarm_f6_config_drift_debugger.py",
]

tools_dir = Path(__file__).parent

for filename in files:
    filepath = tools_dir / filename
    if filepath.exists():
        content = filepath.read_text(encoding="utf-8")
        # Replace emojis with [ICON]
        new_content = EMOJI_PATTERN.sub("[ICON]", content)
        # Also fix specific unicode check marks
        new_content = new_content.replace("✓", "[OK]")
        new_content = new_content.replace("✗", "[FAIL]")
        new_content = new_content.replace("⚠", "[WARN]")
        new_content = new_content.replace("🔍", "[SEARCH]")
        new_content = new_content.replace("📁", "[FOLDER]")
        new_content = new_content.replace("📋", "[LIST]")
        new_content = new_content.replace("📄", "[DOC]")
        new_content = new_content.replace("🔬", "[DEBUG]")
        
        if content != new_content:
            filepath.write_text(new_content, encoding="utf-8")
            print(f"Fixed: {filename}")
        else:
            print(f"No changes: {filename}")
    else:
        print(f"Not found: {filename}")

print("Done!")
