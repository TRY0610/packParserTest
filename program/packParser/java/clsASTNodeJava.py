from ..core.clsASTNode import Node

class ClassNode(Node):
    def __init__(self, children, name=""):
        self.name = name
        self.children = children

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, children={self.children})"

class FunctionNode(Node):
    def __init__(self, name, children):
        self.name = name
        self.children = children

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, children={self.children})"

class IfNode(Node):
    def __init__(self, conditions, trueChildren, falseChildren=None, label=None):
        self.conditions = conditions
        self.trueChildren = trueChildren
        self.falseChildren = falseChildren
        self.label = label

    def __repr__(self):
        return f"{self.__class__.__name__}(label={self.label}, true={self.trueChildren}, false={self.falseChildren})"

class SwitchNode(Node):
    def __init__(self, condition, cases, defaultCase=None, label=None):
        self.condition = condition
        self.cases = cases
        self.defaultCase = defaultCase
        self.label = label

    def __repr__(self):
        return f"{self.__class__.__name__}(label={self.label}, condition={self.condition}, cases={self.cases}, default={self.defaultCase})"

class CaseNode(Node):
    def __init__(self, label, children):
        self.label = label
        self.children = children

    def __repr__(self):
        return f"{self.__class__.__name__}(label={self.label}, children={self.children})"

class LabelNode(Node):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text})"

class CommentNode(Node):
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"{self.__class__.__name__}({self.text})"
        
class StatementNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"{self.__class__.__name__}({self.children})"

class LoopNode(Node):
    def __init__(self, loop_type, conditions, children):
        self.loop_type = loop_type  # "FOR" または "WHILE"
        self.conditions = conditions  # ループの継続条件
        self.children = children      # ループ内のステートメント群
    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.loop_type}, cond={self.conditions}, children={self.children})"