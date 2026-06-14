class BaseParser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0

	def parse(self):
		"""
		各言語パーサ（MarkdownParser, SQLParser）が
		このメソッドを上書きして、AST を返す。
		"""
		raise NotImplementedError
	
	# ---------------------------------------------
	# 現在のノードを取得(移動なし)
	# ---------------------------------------------
	def cur(self):
		return self.tokens[self.pos]

	# ---------------------------------------------
	# 現在のノードを検証
	# ---------------------------------------------
	def at(self, type_):
		return self.cur().type == type_

	# ---------------------------------------------
	# 指定したオフセット先のトークンを取得（移動なし）
	# ---------------------------------------------
	def look_ahead(self, offset=1):
		"""
		現在の位置から offset 分だけ先のトークンを取得する。
		トークン配列の範囲外（EOF以降など）にアクセスしようとした場合は、
		安全のために最後のトークン（通常はEOF）を返す。
		"""
		target_pos = self.pos + offset
		if target_pos >= len(self.tokens):
			return self.tokens[-1]
		return self.tokens[target_pos]

	# ---------------------------------------------
	# 【新規追加】指定したオフセット先のトークンタイプを検証
	# ---------------------------------------------
	def at_ahead(self, type_, offset=1):
		"""
		現在の位置から offset 分だけ先のトークンタイプが type_ と一致するか検証する。
		"""
		return self.look_ahead(offset).type == type_
	
	# ---------------------------------------------
	# 現在のノードを取得(移動あり) 取得したノードを検証→不一致の場合エラー
	# ---------------------------------------------
	def consume(self, type_=None):
		tok = self.cur()
		if type_ and tok.type != type_:
			raise Exception(f"Expected {type_} but got {tok.type}")
		self.pos += 1
		return tok
	
	# ---------------------------------------------
	# 終わりの検証
	# ---------------------------------------------
	def eof(self):
		return self.at("EOF")