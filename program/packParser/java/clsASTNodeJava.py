from ..core.clsASTNode import Node

class ClassNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"

class FunctionNode(Node):
    def __init__(self, name, children):
        self.name = name
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"

class IfNode(Node):
    def __init__(self, conditions, trueChildren, falseChildren = None, label = "", branchLabel = ""):
        self.conditions = conditions
        self.trueChildren = trueChildren
        self.falseChildren = falseChildren
        self.label = label
        self.branchLabel = branchLabel
    def __repr__(self):
        return f"{self.__class__.__name__}(true = {self.trueChildren}, false = {self.falseChildren})"

class CommentNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"
