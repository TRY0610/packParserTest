import re
import inspect
from ..core.clsBaseParser import BaseParser

from .clsASTNodeJava import (
    ClassNode,
    FunctionNode,
    IfNode,
    CommentNode,
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
            # 改行やスペースなどのゴミをスキップ
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue
                
            # 関数（メソッド）の解析を試みる
            function_block = self.parse_function()
            if function_block:
                nodes.append(function_block)
            else:
                # 関数の外にあるトークン（class宣言など）は読み飛ばす
                self.consume()
                
        print("--- Java解析終了 ---")
        return ClassNode(nodes)

    # ---------------------------------------------
    # 関数（メソッド）解析
    # ---------------------------------------------
    def parse_function(self):
        name_tokens = []
        
        # 開き波括弧 '{' に出会うまでを「関数名/シグネチャ」のバッファとする
        while not self.eof() and not self.at("BRACES_OPEN"):
            # 最低限、途中の改行などは無視してトークンの値を集める
            t = self.consume()
            if t.type not in ["NEWLINE", "SPACE"]:
                name_tokens.append(t.value)
                
        if self.eof():
            return None
            
        function_name = " ".join(name_tokens).strip()
        print(f"[関数発見]: {function_name}")
        
        # '{' を消費
        self.consume("BRACES_OPEN")
        
        # 関数の中身（ステートメントの集まり）をパース
        # 閉じ波括弧 '}' が来るまで読み進める
        children = self.parse_statements("BRACES_CLOSE")
        
        # '}' を消費
        if self.at("BRACES_CLOSE"):
            self.consume("BRACES_CLOSE")
            
        return FunctionNode(function_name, children)

    # ---------------------------------------------
    # ステートメント群の共通解析（ブロックの中身用）
    # ---------------------------------------------
    def parse_statements(self, end_token_type):
        """指定した終了トークンが来るまで、中身を再帰的にパースする"""
        nodes = []
        while not self.eof() and not self.at(end_token_type):
            if self.at("NEWLINE") or self.at("SPACE"):
                self.consume()
                continue
                
            if self.at("IF"):
                nodes.append(self.parse_if())
            elif self.at("COMMENT"):
                nodes.append(self.parse_comment())
            elif self.at("COMMENT_MULTI_LINE_OPEN"):
                nodes.append(self.parse_multi_comment())
            else:
                # 分岐でもコメントでもない、普通の1行の処理文（例: showDashboard();）
                # Mermaidの箱（ActionNodeのようなもの）にするためにテキストを収集
                action_text = ""
                while not self.eof() and not self.at("NEWLINE") and not self.at("BRACES_CLOSE"):
                    # 次に急にIFやCOMMENTが来たら中断する安全弁
                    if self.at("IF") or self.at("COMMENT") or self.at("COMMENT_MULTI_LINE_OPEN"):
                        break
                    action_text += self.consume().value
                
                action_text = action_text.strip()
                if action_text:
                    # 本来はActionNodeなどを作ると良いですが、
                    # いったんCommentNodeを流用、またはテキストとしてログ出力します
                    print(f"  [処理文]: {action_text}")
                    nodes.append(CommentNode(action_text)) # 仮で箱に入れておく
                    
        return nodes

    # ---------------------------------------------
    # IF文解析
    # ---------------------------------------------
    def parse_if(self):
        self.consume("IF")
        print("  [IF文解析開始]")
        
        # 条件式 ( ... ) の中身を抽出
        condition_text = ""
        if self.at("SPACE"): self.consume()
        
        if self.at("PAREN_OPEN"):
            self.consume("PAREN_OPEN")
            # 閉じ括弧が来るまで条件式テキストを集める
            paren_depth = 1
            while not self.eof() and paren_depth > 0:
                if self.at("PAREN_OPEN"): paren_depth += 1
                if self.at("PAREN_CLOSE"): paren_depth -= 1
                
                t = self.consume()
                if paren_depth > 0:
                    condition_text += t.value
                elif paren_depth == 0 and t.type != "PAREN_CLOSE":
                    # 安全のため
                    condition_text += t.value
                    
        print(f"    条件式: {condition_text.strip()}")
        
        # ifの中身（Trueブロック）のパース
        while not self.eof() and not self.at("BRACES_OPEN"):
            self.consume() # スペースや改行のスキップ
            
        self.consume("BRACES_OPEN")
        true_children = self.parse_statements("BRACES_CLOSE")
        self.consume("BRACES_CLOSE")
        
        # else / else if の解析
        false_children = []
        while not self.eof() and (self.at("SPACE") or self.at("NEWLINE")):
            self.consume()
            
        if self.at("ELSE"):
            self.consume("ELSE")
            while not self.eof() and (self.at("SPACE") or self.at("NEWLINE")):
                self.consume()
                
            if self.at("IF"):
                # 「else if」の場合は、false_children の中にさらに IfNode をネストさせる
                print("    [else if を発見]")
                false_children.append(self.parse_if())
            else:
                # 単なる「else」の場合
                print("    [else ブロック解析]")
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
        
        # 行末（NEWLINE）が来るまでをコメントの内容とする
        while not self.eof() and not self.at("NEWLINE"):
            comment_text += self.consume().value
            
        print(f"  [単行コメント]: {comment_text.strip()}")
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
            
        print(f"  [複数行コメント]: {comment_text.strip()}")
        return CommentNode(comment_text.strip())