import sys

with open('autoBMAD/epic_automation/dev_agent.py', 'r') as f:
    content = f.read()

old_check = '''    def _check_claude_available(self) -> bool:
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

new_check = '''    def _check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            # Try multiple approaches to find claude
            import os
            
            # First, try direct path for Windows
            possible_paths = [
                r'C:\Users\Administrator\AppData\Roaming\npm\claude',
                r'C:\Users\Administrator\AppData\Roaming\npm\claude.cmd',
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
            
            # If direct path fails, try 'where' command
            try:
                result = subprocess.run(
                    ['where', 'claude'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    # Found path, verify it works
                    claude_path = result.stdout.strip().split('\n')[0]
                    verify = subprocess.run(
                        [claude_path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True
                    )
                    if verify.returncode == 0:
                        logger.info(f"Claude Code CLI available: {verify.stdout.strip()}")
                        return True
            except Exception:
                pass
            
            return False
        except Exception as e:
            logger.warning(f"Claude Code CLI not available: {e}")
            return False'''

content = content.replace(old_check, new_check)

with open('autoBMAD/epic_automation/dev_agent.py', 'w') as f:
    f.write(content)

print("File updated with better claude detection")
