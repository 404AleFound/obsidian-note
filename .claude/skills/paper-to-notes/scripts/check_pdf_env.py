"""检查 paper-reading 所需的 PDF 文本提取库是否可用。

本脚本只读取 Python 的模块发现信息，不读取 PDF、不写入文件，也不安装依赖。
"""

import importlib.util


MODULES = ("pypdf", "PyPDF2", "fitz", "pdfplumber", "pdfminer")


def main() -> None:
    for module_name in MODULES:
        available = importlib.util.find_spec(module_name) is not None
        print(f"{module_name}: {available}")


if __name__ == "__main__":
    main()
