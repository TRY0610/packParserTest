class ASTNode:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f"ASTNode({self.type})"
# ============================================================
# AST Node Definitions
# ============================================================

class Node:
    """全 AST ノードの基底クラス"""
    pass

