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
	# 現在のノードを取得(移動あり)　取得したノードを検証→不一致の場合エラー
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