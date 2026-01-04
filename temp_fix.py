import sys

with open('autoBMAD/epic_automation/dev_agent.py', 'r') as f:
    content = f.read()

old_method = '''    def _check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True  # Required for Windows
            )
            if result.returncode == 0:
                logger.info(f"Claude Code CLI available: {result.stdout.strip()}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Claude Code CLI not available: {e}")
            return False'''

new_method = '''    def _check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            # First try 'where' command on Windows, then 'which' on Unix
            commands_to_try = [
                ['where', 'claude'],
                ['which', 'claude'],
                ['claude', '--version']
            ]

            for cmd in commands_to_try:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True  # Required for Windows
                    )
                    if result.returncode == 0:
                        # If it's a version check, verify it works
                        if cmd[0] == 'claude':
                            logger.info(f"Claude Code CLI available: {result.stdout.strip()}")
                        else:
                            # Path found, now verify claude works
                            verify = subprocess.run(
                                ['claude', '--version'],
                                capture_output=True,
                                text=True,
                                timeout=10,
                                shell=True
                            )
                            if verify.returncode == 0:
                                logger.info(f"Claude Code CLI available: {verify.stdout.strip()}")
                            else:
                                continue
                        return True
                except Exception:
                    continue

            return False
        except Exception as e:
            logger.warning(f"Claude Code CLI not available: {e}")
            return False'''

content = content.replace(old_method, new_method)

with open('autoBMAD/epic_automation/dev_agent.py', 'w') as f:
    f.write(content)

print("File updated successfully")
