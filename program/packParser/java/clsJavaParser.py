import re
import inspect
from ..core.clsBaseParser import BaseParser

from .clsASTNodeJava import (
    ClassNode,
    FunctionNode,
    IfNode,
    SwitchNode,
    CaseNode,
    CommentNode,
    LabelNode,
    StatementNode,
    LoopNode,
)

class JavaParser(BaseParser):
    def __init__(self, tokens):
        super().__init__(tokens)

    # ---------------------------------------------
    # 解析処理の開始
    # ---------------------------------------------
    def parse(self):
        nodes = []
        while not self.eof():
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue

            if self.at("CLASS"):
                nodes.append(self.parse_class())
                continue

            function_block = self.parse_function()
            if function_block:
                nodes.append(function_block)
            else:
                self.consume()

        return ClassNode(nodes)

    # ---------------------------------------------
    # クラス解析
    # ---------------------------------------------
    def parse_class(self):
        self.consume("CLASS")
        name_tokens = []
        while not self.eof() and not self.at("BRACES_OPEN"):
            name_tokens.append(self.consume().value)

        class_name = " ".join(name_tokens).strip()
        self.consume("BRACES_OPEN")

        children = self.parse_statements("BRACES_CLOSE")
        self.consume("BRACES_CLOSE")

        return ClassNode(children, class_name)

    # ---------------------------------------------
    # 関数（メソッド）解析
    # ---------------------------------------------
    def parse_function(self):
        start_pos = self.pos
        name_tokens = []
        while not self.eof() and not self.at("BRACES_OPEN") and not self.at("SEMICOLON") and not self.at("NEWLINE"):
            name_tokens.append(self.consume().value)

        if self.eof() or not self.at("BRACES_OPEN"):
            self.pos = start_pos
            return None

        name = " ".join(name_tokens).strip()
        self.consume("BRACES_OPEN")

        children = self.parse_statements("BRACES_CLOSE")
        self.consume("BRACES_CLOSE")

        return FunctionNode(name, children)

    # ---------------------------------------------
    # 複数ステートメントの解析ループ
    # ---------------------------------------------
    def parse_statements(self, close_token_type):
        nodes = []
        while not self.eof() and not self.at(close_token_type):
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue

            node = self.parse_function_block()
            if node:
                nodes.append(node)
        return nodes

    # ---------------------------------------------
    # ブロック内部要素の解析分岐
    # ---------------------------------------------
    def parse_function_block(self):
        if self.at("FOR") or self.at("WHILE"):
            return self.parse_loop()

        if self.at("IF"):
            return self.parse_if()

        if self.at("SWITCH"):
            return self.parse_switch()

        if self.at("CLASS"):
            return self.parse_class()

        if self.at("COMMENT"):
            return self.parse_comment()

        if self.at("COMMENT_MULTI_LINE_OPEN"):
            return self.parse_multi_comment()

        return self.parse_statement()

    # ---------------------------------------------
    # 文（ステートメント）解析
    # ---------------------------------------------
    def parse_statement(self):
        statement_tokens = []
        while not self.eof() and not self.at("SEMICOLON") and not self.at("NEWLINE") and not self.at("BRACES_CLOSE") and not self.at("CASE") and not self.at("DEFAULT") and not self.at("BRACES_OPEN"):
            statement_tokens.append(self.consume().value)

        if self.at("SEMICOLON"):
            statement_tokens.append(self.consume().value)

        statement_text = "".join(statement_tokens).strip()
        return StatementNode(statement_text)
    
    # ---------------------------------------------
    # FOR / WHILE ループ解析
    # ---------------------------------------------
    def parse_loop(self):
        loop_type = "FOR" if self.at("FOR") else "WHILE"
        self.consume()

        while not self.eof() and not self.at("PAREN_OPEN"):
            self.consume()

        condition_tokens = []
        self.consume("PAREN_OPEN")
        paren_depth = 1

        while not self.eof() and paren_depth > 0:
            if self.at("PAREN_OPEN"):
                paren_depth += 1
            elif self.at("PAREN_CLOSE"):
                paren_depth -= 1
                if paren_depth == 0:
                    self.consume("PAREN_CLOSE")
                    break
            condition_tokens.append(self.consume().value)

        condition_text = "".join(condition_tokens)

        while not self.eof() and (self.at("NEWLINE") or self.at("SPACE")):
            self.consume()

        if self.at("BRACES_OPEN"):
            self.consume("BRACES_OPEN")
            children = self.parse_statements("BRACES_CLOSE")
            self.consume("BRACES_CLOSE")
        else:
            stmt = self.parse_function_block()
            children = [stmt] if stmt else []

        return LoopNode(loop_type, condition_text.strip(), children)

    # ---------------------------------------------
    # IF解析
    # ---------------------------------------------
    def parse_if(self, label=None):
        self.consume("IF")

        while not self.eof() and not self.at("PAREN_OPEN"):
            self.consume()

        condition_tokens = []
        self.consume("PAREN_OPEN")
        paren_depth = 1

        while not self.eof() and paren_depth > 0:
            if self.at("PAREN_OPEN"):
                paren_depth += 1
            elif self.at("PAREN_CLOSE"):
                paren_depth -= 1
                if paren_depth == 0:
                    self.consume("PAREN_CLOSE")
                    break
            condition_tokens.append(self.consume().value)

        condition_text = "".join(condition_tokens)

        while not self.eof() and (self.at("NEWLINE") or self.at("SPACE")):
            self.consume()

        if self.at("BRACES_OPEN"):
            self.consume("BRACES_OPEN")
            true_children = self.parse_statements("BRACES_CLOSE")
            self.consume("BRACES_CLOSE")
        else:
            stmt = self.parse_function_block()
            true_children = [stmt] if stmt else []

        false_children = None
        pending_false_label = None

        while not self.eof():
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue

            if self.at("COMMENT"):
                comment = self.parse_comment()
                if isinstance(comment, LabelNode):
                    pending_false_label = comment.text
                else:
                    true_children.append(comment)
                continue

            if self.at("COMMENT_MULTI_LINE_OPEN"):
                comment = self.parse_multi_comment()
                if isinstance(comment, LabelNode):
                    pending_false_label = comment.text
                else:
                    true_children.append(comment)
                continue

            break

        if self.at("ELSE"):
            self.consume("ELSE")

            while not self.eof() and (self.at("NEWLINE") or self.at("SPACE")):
                self.consume()

            if self.at("IF"):
                nested_if = self.parse_if(label=pending_false_label)
                false_children = [nested_if]
            elif self.at("BRACES_OPEN"):
                self.consume("BRACES_OPEN")
                false_children = self.parse_statements("BRACES_CLOSE")
                self.consume("BRACES_CLOSE")
                if pending_false_label and false_children:
                    first = false_children[0]
                    if hasattr(first, 'label'):
                        first.label = pending_false_label
            else:
                stmt = self.parse_function_block()
                false_children = [stmt] if stmt else []
                if pending_false_label and false_children and hasattr(false_children[0], 'label'):
                    false_children[0].label = pending_false_label

        node = IfNode(condition_text.strip(), true_children, false_children)
        if label:
            node.label = label
        return node

    # ---------------------------------------------
    # SWITCH解析
    # ---------------------------------------------
    def parse_switch(self):
        self.consume("SWITCH")

        while not self.eof() and not self.at("PAREN_OPEN"):
            self.consume()

        condition_tokens = []
        self.consume("PAREN_OPEN")
        paren_depth = 1

        while not self.eof() and paren_depth > 0:
            if self.at("PAREN_OPEN"):
                paren_depth += 1
            elif self.at("PAREN_CLOSE"):
                paren_depth -= 1
                if paren_depth == 0:
                    self.consume("PAREN_CLOSE")
                    break
            condition_tokens.append(self.consume().value)

        condition_text = "".join(condition_tokens)

        while not self.eof() and (self.at("NEWLINE") or self.at("SPACE")):
            self.consume()

        if self.at("BRACES_OPEN"):
            self.consume("BRACES_OPEN")

        cases = []
        default_case = None

        while not self.eof() and not self.at("BRACES_CLOSE"):
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue

            if self.at("CASE"):
                cases.append(self.parse_case())
                continue

            if self.at("DEFAULT"):
                default_case = self.parse_default()
                continue

            if cases:
                cases[-1].children.extend(self.parse_case_body())
            elif default_case:
                default_case.children.extend(self.parse_case_body())
            else:
                self.consume()

        self.consume("BRACES_CLOSE")
        return SwitchNode(condition_text.strip(), cases, default_case)

    def parse_case(self):
        self.consume("CASE")
        label_tokens = []
        while not self.eof() and not self.at("COLON"):
            label_tokens.append(self.consume().value)

        if self.at("COLON"):
            self.consume("COLON")

        label_text = "".join(label_tokens).strip()
        children = self.parse_case_body()
        return CaseNode(label_text, children)

    def parse_default(self):
        self.consume("DEFAULT")
        while not self.eof() and not self.at("COLON"):
            self.consume()

        if self.at("COLON"):
            self.consume("COLON")

        children = self.parse_case_body()
        return CaseNode("default", children)

    def parse_case_body(self):
        children = []
        while not self.eof() and not self.at("BRACES_CLOSE") and not self.at("CASE") and not self.at("DEFAULT"):
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue

            child = self.parse_function_block()
            if child:
                children.append(child)

        return children

    # ---------------------------------------------
    # 単一行コメント解析 (// ...)
    # ---------------------------------------------
    def parse_comment(self):
        self.consume("COMMENT")
        comment_text = ""
        while not self.eof() and not self.at("NEWLINE"):
            comment_text += self.consume().value

        raw = comment_text.strip()
        if raw.startswith("@"):
            return LabelNode(raw[1:].strip())

        return CommentNode(raw)

    # ---------------------------------------------
    # 複数行コメント解析 (/* ... */)
    # ---------------------------------------------
    def parse_multi_comment(self):
        self.consume("COMMENT_MULTI_LINE_OPEN")
        comment_text = ""
        while not self.eof() and not self.at("COMMENT_MULTI_LINE_CLOSE"):
            comment_text += self.consume().value
            
        if self.at("COMMENT_MULTI_LINE_CLOSE"):
            self.consume("COMMENT_MULTI_LINE_CLOSE")
            
        raw = comment_text.strip()
        if raw.startswith("@"):
            return LabelNode(raw[1:].strip())

        return CommentNode(raw)