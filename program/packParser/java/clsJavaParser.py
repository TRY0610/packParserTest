import re
import inspect
from ..core.clsBaseParser import BaseParser

from .clsASTNodeJava import (
    ClassNode,
    FunctionNode,
    IfNode,
    CommentNode,
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
        print("--- Java解析開始 ---")
        while not self.eof():
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue
                
            function_block = self.parse_function()
            if function_block:
                nodes.append(function_block)
            else:
                self.consume()
                
        print("--- Java解析終了 ---")
        return ClassNode(nodes)

    # ---------------------------------------------
    # 関数（メソッド）解析
    # ---------------------------------------------
    def parse_function(self):
        name_tokens = []
        while not self.eof() and not self.at("BRACES_OPEN"):
            name_tokens.append(self.consume().value)
        
        if self.eof():
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
            
        if self.at("COMMENT"):
            return self.parse_comment()
            
        if self.at("COMMENT_MULTI_LINE_OPEN"):
            return self.parse_multi_comment()
            
        # 【修正点】IFでもコメントでもないトークン（通常の処理文など）が来たら
        # Java解析器の責任として、「StatementNode（処理文ノード）」として正しくパースする
        stmt_token = self.consume()
        return StatementNode(stmt_token.value)
    
    # ---------------------------------------------
    # FOR / WHILE ループ解析
    # ---------------------------------------------
    def parse_loop(self):
        # FOR か WHILE かを保持
        loop_type = "FOR" if self.at("FOR") else "WHILE"
        self.consume() # トークンを消費
        
        # 条件式の始まり ( までスキップ
        while not self.eof() and not self.at("PAREN_OPEN"):
            self.consume()
            
        condition_tokens = []
        self.consume("PAREN_OPEN")
        paren_depth = 1
        
        # 括弧のネストを考慮して条件式を抽出
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
        
        # ブロックの始まり { までスキップ
        while not self.eof() and not self.at("BRACES_OPEN"):
            self.consume()
            
        self.consume("BRACES_OPEN")
        children = self.parse_statements("BRACES_CLOSE")
        self.consume("BRACES_CLOSE")
        
        return LoopNode(loop_type, condition_text.strip(), children)
    
    # ---------------------------------------------
    # IF解析
    # ---------------------------------------------
    def parse_if(self):
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
        
        while not self.eof() and not self.at("BRACES_OPEN"):
            self.consume()
            
        self.consume("BRACES_OPEN")
        true_children = self.parse_statements("BRACES_CLOSE")
        self.consume("BRACES_CLOSE")
        
        false_children = None
        
        while not self.eof() and (self.at("NEWLINE") or self.at("SPACE")):
            self.consume()
            
        if self.at("ELSE"):
            self.consume("ELSE")
            
            while not self.eof() and (self.at("NEWLINE") or self.at("SPACE")):
                self.consume()
                
            if self.at("IF"):
                # else if の場合はネストされたIfNodeとして解析
                false_children = [self.parse_if()]
            else:
                if self.at("BRACES_OPEN"):
                    self.consume("BRACES_OPEN")
                    false_children = self.parse_statements("BRACES_CLOSE")
                    self.consume("BRACES_CLOSE")
                    
        return IfNode(condition_text.strip(), true_children, false_children)

    # ---------------------------------------------
    # 単一行コメント解析 (// ...)
    # ---------------------------------------------
    def parse_comment(self):
        self.consume("COMMENT")
        comment_text = ""
        while not self.eof() and not self.at("NEWLINE"):
            comment_text += self.consume().value
        return CommentNode(comment_text.strip())

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
            
        return CommentNode(comment_text.strip())