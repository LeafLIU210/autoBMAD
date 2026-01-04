import sys

with open('autoBMAD/epic_automation/dev_agent.py', 'r') as f:
    content = f.read()

# Find and replace the _check_claude_available method
import re

pattern = r'(    def _check_claude_available\(self\) -> bool:.*?return False\n        except Exception as e:\n            logger\.warning\(f"Claude Code CLI not available: \{e\}"\)\n            return False)'

replacement = r'''    def _check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            # Try direct path for Windows
            possible_paths = [
                r''' + r'C:\Users\Administrator\AppData\Roaming\npm\claude' + ''',
                r''' + r'C:\Users\Administrator\AppData\Roaming\npm\claude.cmd' + ''',
                'claude'
            ]
            
            for claude_cmd in possible_paths:
                try:
                    result = subprocess.run(
                        [claude_cmd, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True
                    )
                    if result.returncode == 0:
                        logger.info(f"Claude Code CLI available: {result.stdout.strip()}")
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            logger.warning(f"Claude Code CLI not available: {e}")
            return False'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('autoBMAD/epic_automation/dev_agent.py', 'w') as f:
    f.write(content)

print("File updated")
