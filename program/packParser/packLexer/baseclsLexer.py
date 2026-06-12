import re
from .clsToken import Token

'''
字句解析クラス
'''
class BaseLexer:
	# コンストラクタ
	def __init__(self, text, token_defs):
		self.text = text
		self.pos = 0
		self.length = len(text)
		self.token_defs = token_defs  # [{ "type": "...", "regex": r"...", "ignore": bool }]
	
	# 終了判定
	def is_eof(self):
		return self.pos >= self.length
	
	# ---------------------------------------------
	# 字句解析
	# ---------------------------------------------
	def next_token(self):
		# 最後まで解析した場合、終了
		# (tokenizeではそもそも終了状態で呼ばれることはないが、念のための処理)
		if self.is_eof():
			return Token("EOF", None, self.pos)
		
		# 現在位置以降の文字列
		remaining = self.text[self.pos:]
		
		# 正規表現で一つずつ検索
		for token_def in self.token_defs:
			# 正規表現の取得と実行
			pattern = token_def["regex"]
			regex = re.compile(pattern)
			match = regex.match(remaining)
			
			# 正規表現の結果確認
			if match:
				# マッチした情報を取得
				value = match.group(0)
				token_type = token_def["type"]
				ignore = token_def.get("ignore", False)
				
				# 現在位置を進める
				self.pos += len(value)
				
				# 無視する場合は現在の情報を返さず、次のトークンを探す
				if ignore:
					return self.next_token()
				
				# 現在のトークンを返して終了
				return Token(token_type, value, self.pos)
		
		# ここまで到達した場合、正規表現にヒットしない文字が存在しているため、エラーを戻す
		raise Exception(f"Lexer error at position {self.pos}: {remaining[0]!r}")
	
	# ---------------------------------------------
	# 字句解析実行
	# ---------------------------------------------
	def tokenize(self):
		tokens = []
		
		# 最後まで繰り返し
		while not self.is_eof():
			tokens.append(self.next_token())
		
		# 終了字句追加
		tokens.append(Token("EOF", None, self.pos))
		
		return tokens
