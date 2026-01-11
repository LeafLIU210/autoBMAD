"""BasedPyright CLI 入口模块.

提供命令行接口，支持 check, report, fix, workflow 等命令。
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
