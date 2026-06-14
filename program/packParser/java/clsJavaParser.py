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
		print("解析開始")
		while not self.eof():
			# ブロックを処理
			function_block = self.parse_function()
			
			if function_block:
				# 追加
				nodes.append(function_block)
		print("解析終了")
		return ClassNode(nodes)

	# ---------------------------------------------
	# 関数解析
	# ---------------------------------------------
	def parse_function(self):
		name = ""
		childrens=[]
		
		print("関数名作成")
		while (
			not self.eof()
			and not self.at("BRACES_OPEN")
		):
			name += self.consume().value
		print(f"関数名作成{name}")
		
		self.consume("BRACES_OPEN")
		
		print(f"中身解析")
		while (
			not self.eof()
			and not self.at("BRACES_CLOSE")
		):
			children = self.parse_function_block()
		
			if children:
				# 追加
				childrens.append(children)
		
		print(f"中身解析終了")
		self.consume("BRACES_CLOSE")
		
		return FunctionNode(name, childrens)
	
	# ---------------------------------------------
	# 処理解析
	# ---------------------------------------------
	def parse_function_block(self):
		if self.at("IF"):
			print(f"IFトークン")
			return self.parse_if()
		if self.at("COMMENT"):
			print(f"コメントトークン")
			return self.parse_comment()
		
		self.consume()
		return None
	
	# ---------------------------------------------
	# IF解析
	# ---------------------------------------------
	def parse_if(self):
		print(f"IF開始")
		while (
			not self.eof()
			and not self.at("PAREN_OPEN")
		):
			self.consume()
		
		conditions = self.get_bracket_intext("PAREN_OPEN", "PAREN_CLOSE")
		
		self.consume("BRACES_OPEN")
		nodes = []
		
		while (
			not self.eof()
			and not self.at("BRACES_CLOSE")
		):
			trueNode = self.parse_function_block()
			if trueNode:
				# 追加
				nodes.append(trueNode)
		
		self.consume("BRACES_CLOSE")
		
		print(f"条件 {conditions}")
		return None
	
	# ---------------------------------------------
	# コメント解析
	# ---------------------------------------------
	def parse_comment(self):
		self.consume("COMMENT")
		text=""
		
		while (
			not self.eof()
			and not self.at("NEWLINE")
		):
			text += self.consume().value
		
		self.at("NEWLINE")
		print(f"コメント{text}")
		
		return CommentNode(text)
	
	# ---------------------------------------------
	# カッコ内取得
	# ---------------------------------------------
	def get_bracket_intext(self, open, close):
		text=""
		index = 0
		
		self.consume(open)
		
		while (
			not self.eof()
		):
			if self.at(open):
				i+=1
			if self.at(close):
				if index == 0:
					break
				else:
					i-=1
			text += self.consume().value
		
		self.consume(close)
		
		return text
