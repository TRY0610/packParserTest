# packParser/Java/__init__.py

# ① 内部のファイル（LexerやParser）を読み込む
from .clsJavaLexer import executeJavaLexer
from .clsJavaParser import JavaParser
from .clsRendererMermaid import RendererMermaid
from ..clsFileManager import clsFileManager

# ② メインプログラム（外側）に公開する「窓口」を定義する
# ※ ここに core のクラス（BaseParserなど）は絶対に含めない！
__all__ = [
    "executeJavaLexer",
    "JavaParser",
    "RendererMermaid",
    "clsFileManager",
]