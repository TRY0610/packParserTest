import re
import inspect
'''
# -------------------------------------------------
# Token class (Lexerと共通)
# -------------------------------------------------
class Token:
	def __init__(self, type_, value):
		self.type = type_
		self.value = value

	def __repr__(self):
		return f"Token({self.type}, {self.value})"

# -------------------------------------------------
# Node classes (AST用)
# -------------------------------------------------
class DocumentNode:
	def __init__(self, children):
		self.children = children

	def __repr__(self):
		return f"Document({self.children})"

class HeadingNode:
	def __init__(self, level, children):
		self.level = level
		self.children = children

	def __repr__(self):
		return f"H{self.level}({self.children})"

class ParagraphNode:
	def __init__(self, children):
		self.children = children

	def __repr__(self):
		return f"Paragraph({self.children})"

class BoldNode:
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return f"Bold({self.text})"

class TextNode:
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return f"Text({self.text})"

# -------------------------------------------------
# Parser
# -------------------------------------------------
class MarkdownParser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0

	# ---------------------------------------------
	# Utility
	# ---------------------------------------------
	def peek(self):
		"""次のトークンを返す（カーソルは進めない）"""
		if self.pos < len(self.tokens):
			return self.tokens[self.pos]
		return None

	def consume(self, type_=None):
		"""現在のトークンを返してカーソルを1つ進める"""
		token = self.peek()
		if token is None:
			return None
		if type_ and token.type != type_:
			raise ValueError(f"Expected token {type_}, got {token.type}")
		self.pos += 1
		return token

	# ---------------------------------------------
	# 構文解析開始
	# ---------------------------------------------
	def parse(self):
		print(inspect.currentframe().f_code.co_name)
		children = []
		while self.peek() is not None:
			if self.peek().type == "HASH":
				children.append(self.parse_heading())
			else:
				children.append(self.parse_paragraph())
		return DocumentNode(children)

	# ---------------------------------------------
	# 段落タイトル: # text
	# ---------------------------------------------
	def parse_heading(self):
		print(inspect.currentframe().f_code.co_name)
		hash_token = self.consume("HASH")
		level = len(hash_token.value)

		children = []
		while self.peek() and self.peek().type != "NEWLINE":
			children.extend(self.parse_inline())

		self.consume("NEWLINE") if self.peek() and self.peek().type == "NEWLINE" else None
		return HeadingNode(level, children)

	# ---------------------------------------------
	# 段落
	# ---------------------------------------------
	def parse_paragraph(self):
		print(inspect.currentframe().f_code.co_name)
		children = []

		while self.peek() and self.peek().type != "NEWLINE" and self.peek().type != "HASH":
			children.extend(self.parse_inline())

		self.consume("NEWLINE") if self.peek() and self.peek().type == "NEWLINE" else None
		return ParagraphNode(children)

	# ---------------------------------------------
	# インライン装飾 （Text / Bold）
	# ---------------------------------------------
	def parse_inline(self):
		print(inspect.currentframe().f_code.co_name)
		token = self.peek()

		if token.type == "BOLD":
			self.consume("BOLD")
			text = token.value.strip("*")
			return [BoldNode(text)]

		elif token.type == "TEXT":
			self.consume("TEXT")
			return [TextNode(token.value)]

		return []

# -------------------------------------------------
# 動作テスト
# -------------------------------------------------
if __name__ == "__main__":
	tokens = [Token(TEXT, 'こんにちは')
		, Token(BOLD, '**')
		, Token(TEXT, 'eei')
		, Token(BOLD, '**')
		, Token(TEXT, ' ')
		, Token(NEWLINE, '\n')
		, Token(ITALIC, '*')
		, Token(TEXT, 'ヤッホー')
		, Token(ITALIC, '*)
		, Token(EOF, None)
	]

	parser = MarkdownParser(tokens)
	ast = parser.parse()

	print(ast)
'''
# ============================================================
# AST Node Definitions
# ============================================================

class Node:
    """全 AST ノードの基底クラス"""
    pass

class DocumentNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"Document({self.children})"


# ------------------------------
# Block-level nodes
# ------------------------------
class HeadingNode(Node):
    def __init__(self, level, children):
        self.level = level
        self.children = children
    def __repr__(self):
        return f"H{self.level}({self.children})"

class ParagraphNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"Paragraph({self.children})"

class MetaNode(Node):
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def __repr__(self):
        return f"Meta({self.key}: {self.value})"

class TableNode(Node):
    def __init__(self, rows):
        self.rows = rows
    def __repr__(self):
        return f"Table({self.rows})"

class TableRowNode(Node):
    def __init__(self, cells):
        self.cells = cells
    def __repr__(self):
        return f"Row({self.cells})"


# ------------------------------
# Inline nodes
# ------------------------------
class BoldNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"Bold({self.children})"

class ItalicNode(Node):
    def __init__(self, children):
        self.children = children
    def __repr__(self):
        return f"Italic({self.children})"

class ExternalLinkNode(Node):
    def __init__(self, text, url):
        self.text = text
        self.url = url
    def __repr__(self):
        return f"ExternalLink(text={self.text}, url={self.url})"

class InternalLinkNode(Node):
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"InternalLink({self.text})"

class TextNode(Node):
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"Text({self.text})"


class MarkdownParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # -------------------------
    # Utility
    # -------------------------
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, type_=None):
        token = self.peek()
        if token is None:
            return None
        if type_ and token.type != type_:
            raise ValueError(f"Expected {type_}, got {token.type}")
        self.pos += 1
        return token

    # -------------------------
    # Entry point
    # -------------------------
    def parse(self):
        children = []

        while self.peek():
            tok = self.peek()

            if tok.type == "META":
                children.append(self.parse_meta())

            elif tok.type == "HASH":
                children.append(self.parse_heading())

            elif tok.type == "TABLE_START":
                children.append(self.parse_table())

            else:
                children.append(self.parse_paragraph())

        return DocumentNode(children)

    # -------------------------
    # Meta info  --key:value
    # -------------------------
    def parse_meta(self):
        t = self.consume("META")
        key, value = t.value.split(":", 1)
        return MetaNode(key.strip(), value.strip())

    # -------------------------
    # Heading
    # -------------------------
    def parse_heading(self):
        t = self.consume("HASH")
        level = len(t.value)

        inline = self.parse_inline_until("NEWLINE")
        self.consume("NEWLINE")
        return HeadingNode(level, inline)

    # -------------------------
    # Paragraph
    # -------------------------
    def parse_paragraph(self):
        children = self.parse_inline_until("NEWLINE")
        if self.peek() and self.peek().type == "NEWLINE":
            self.consume("NEWLINE")
        return ParagraphNode(children)

    # -------------------------
    # Table
    # -------------------------
    def parse_table(self):
        self.consume("TABLE_START")  # \table

        rows = []
        while self.peek() and self.peek().type == "TABLE_ROW":
            row = self.consume("TABLE_ROW")
            cells = [c.strip() for c in row.value.strip("|").split("|")]
            rows.append(TableRowNode(cells))
        return TableNode(rows)

    # -------------------------
    # Inline parsing
    # -------------------------
    def parse_inline_until(self, end_type):
        items = []
        while self.peek() and self.peek().type != end_type:
            tok = self.peek()
            if tok.type == "BOLD_START":
                items.append(self.parse_bold())

            elif tok.type == "ITALIC_START":
                items.append(self.parse_italic())

            elif tok.type == "EXTERNAL_LINK":
                items.append(self.parse_external_link())

            elif tok.type == "INTERNAL_LINK":
                items.append(self.parse_internal_link())

            elif tok.type == "TEXT":
                items.append(TextNode(self.consume("TEXT").value))

            else:
                self.consume()  # とりあえず無視

        return items

    # -------------------------
    # Inline nodes
    # -------------------------
    def parse_bold(self):
        self.consume("BOLD_START")  # **

        children = self.parse_inline_until("BOLD_END")
        self.consume("BOLD_END")
        return BoldNode(children)

    def parse_italic(self):
        self.consume("ITALIC_START")  # __
        children = self.parse_inline_until("ITALIC_END")
        self.consume("ITALIC_END")
        return ItalicNode(children)

    def parse_external_link(self):
        tok = self.consume("EXTERNAL_LINK")
        text, url = tok.value
        return ExternalLinkNode(text, url)

    def parse_internal_link(self):
        tok = self.consume("INTERNAL_LINK")
        return InternalLinkNode(tok.value)
