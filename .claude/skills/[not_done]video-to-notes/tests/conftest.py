import sys
from pathlib import Path

# 让测试能 `from ytlt import ...`：把 skill 根目录（本文件父目录）加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
