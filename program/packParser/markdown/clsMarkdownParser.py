import re
import inspect
from ..core.clsBaseParser import BaseParser

from .clsASTNodeMarkdown import (
	DocumentNode,
	HeadingNode,
	MetaNode,
	ParagraphNode,
	TableNode,
	BoldNode,
	ItalicNode,
	LinkNode,
	TextNode,
	SymbolNode
)

class MarkdownParser(BaseParser):
	def __init__(self, tokens):
		super().__init__(tokens)

	# ---------------------------------------------
	# 解析処理の開始
	# ---------------------------------------------
	def parse(self):
		nodes = []
		while not self.eof():
			# ブロックを処理
			block = self.parse_block()
			
			if block:
				# 追加
				nodes.append(block)
		return DocumentNode(nodes)

	# ---------------------------------------------
	# ブロックノード一覧
	# ---------------------------------------------
	def parse_block(self):
		# 現在のノードと一致するブロックを探す
		if self.at("META"):
			return self.parse_meta()

		if self.at("HASH"):
			return self.parse_heading()

		if self.at("TABLE_START"):
			return self.parse_table()
		
		# ※このままだとノートに戻すときに改行がされなくなるため、今後修正する必要がある
		if self.at("NEWLINE"):
			self.consume("NEWLINE")
			return None
		# 
		return self.parse_paragraph()

	# ---------------------------------------------
	# メタノード
	# ---------------------------------------------
	def parse_meta(self):
		tok = self.consume("META")
		key, value = tok.value.split(":")
		# METAは丸ごとテキストで保持
		return MetaNode(key, value)

	# ---------------------------------------------
	# 見出しノード
	# ---------------------------------------------
	def parse_heading(self):
		hash_tok = self.consume("HASH")
		level = len(hash_tok.value)

		inlines = self.parse_inlines_until_newline()

		if self.at("NEWLINE"):
			self.consume("NEWLINE")

		return HeadingNode(level, inlines)

	# ---------------------------------------------
	# テーブルブロック
	# ---------------------------------------------
	def parse_table(self):
		rows = []

		start_tok = self.consume("TABLE_START")

		rows.append(start_tok.value)

		while not self.at("EOF"):
			if self.at("TABLE_ROW"):
				row_tok = self.consume("TABLE_ROW")
				rows.append(row_tok.value)
				continue

			if self.at("NEWLINE"):
				end_tok = self.consume("NEWLINE")
				rows.append(end_tok.value)
				return TableNode("".join(rows))

			# 他のトークンはテーブル中の TEXT として扱う
			rows.append(self.consume().value)

		raise Exception("TABLE_START without TABLE_END")

	# ---------------------------------------------
	# 段落
	# ---------------------------------------------
	def parse_paragraph(self):
		inlines = []

		while (
			not self.eof()
			and not self.at("NEWLINE")
			and not self.at("HASH")
			and not self.at("META")
			and not self.at("TABLE_START")
		):
			inlines.extend(self.parse_inline())

		if self.at("NEWLINE"):
			self.consume("NEWLINE")

		return ParagraphNode(inlines)

	# ---------------------------------------------
	# Inline parsing
	# ---------------------------------------------
	def parse_inlines_until_newline(self):
		parts = []
		while not self.eof() and not self.at("NEWLINE"):
			parts.extend(self.parse_inline())
		return parts

	def parse_inline(self):
		tok = self.cur()

		# ** bold **
		if tok.type == "BOLD_MARK":
			return self.parse_bold()

		# __ italic __
		if tok.type == "ITALIC_MARK":
			return self.parse_italic()

		# [text](url)
		if tok.type == "BRACKET_OPEN":
			return [self.parse_link()]

		# TEXT / SPACE / SYMBOL
		if tok.type == "TEXT":
			return [TextNode(self.consume().value)]

		if tok.type == "SPACE":
			return [TextNode(self.consume().value)]

		if tok.type == "SYMBOL":
			return [SymbolNode(self.consume().value)]

		# fallback
		return [TextNode(self.consume().value)]

	# ---------------------------------------------
	# Inline: Bold
	# ---------------------------------------------
	def parse_bold(self):
		self.consume("BOLD_MARK")
		content = []

		while not self.eof():
			if self.at("BOLD_MARK"):
				self.consume("BOLD_MARK")
				return [BoldNode(content)]
			content.extend(self.parse_inline())

		# 閉じられなかった場合はテキストとして扱う
		return [TextNode("**" + "".join(n.value for n in content))]

	# ---------------------------------------------
	# Inline: Italic
	# ---------------------------------------------
	def parse_italic(self):
		self.consume("ITALIC_MARK")
		content = []

		while not self.eof():
			if self.at("ITALIC_MARK"):
				self.consume("ITALIC_MARK")
				return [ItalicNode(content)]
			content.extend(self.parse_inline())

		# 閉じられず
		return [TextNode("__" + "".join(n.value for n in content))]

	# ---------------------------------------------
	# Inline: Link  [text](url)
	# ---------------------------------------------
	def parse_link(self):
		self.consume("BRACKET_OPEN")

		text_nodes = []
		while not self.eof() and not self.at("BRACKET_CLOSE"):
			text_nodes.extend(self.parse_inline())

		self.consume("BRACKET_CLOSE")

		# 次が ( でなければリンクではなく普通のテキスト扱い
		if not self.at("PAREN_OPEN"):
			return LinkNode(text_nodes)

		self.consume("PAREN_OPEN")

		url = []
		while not self.eof() and not self.at("PAREN_CLOSE"):
			url.append(self.consume().value)

		self.consume("PAREN_CLOSE")

		return LinkNode(text_nodes, "".join(url))
