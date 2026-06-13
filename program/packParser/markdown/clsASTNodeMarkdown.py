from ..core.clsASTNode import Node

class DocumentNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"


# ------------------------------
# Block-level nodes
# ------------------------------
class HeadingNode(Node):
    def __init__(self, level, children):
        self.level = level
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children},level={self.level})"

class ParagraphNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"

class MetaNode(Node):
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def __repr__(self):
        return f"{self.__class__.__name__}(key:{self.key}, value:{self.value})"

class TableNode(Node):
    def __init__(self, rows):
        self.rows = rows
    def __repr__(self):
        return f"{self.__class__.__name__}({self.rows})"

class TableRowNode(Node):
    def __init__(self, cells):
        self.cells = cells
    def __repr__(self):
        return f"{self.__class__.__name__}({self.cells})"


# ------------------------------
# Inline nodes
# ------------------------------
class BoldNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"

class ItalicNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"

class LinkNode(Node):
    def __init__(self, children, url=""):
        self.children = children
        self.url = url
    def __repr__(self):
        return f"{self.__class__.__name__}(children={self.children}, url={self.url})"

'''
class InternalLinkNode(Node):
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"InternalLink({self.text})"
'''

class TextNode(Node):
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"{self.__class__.__name__}({self.text})"

class SymbolNode(Node):
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"{self.__class__.__name__}({self.text})"
