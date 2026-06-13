from ..core.baseclsLexer import BaseLexer

def executeMarkdownLexer(arg_text):
	# 字句の基点となる正規表現一覧
	# 上から順番に判定
	# 
	# キー説明
	# "type": 字句のタイプ
	# "regex": 正規表現
	# "ignore": 無視を行うか(True=無視)
	#
	# 字句タイプ一覧
	# META
	# TABLE_START
	# TABLE_ROW
	# HASH
	# BOLD_MARK
	# ITALIC_MARK
	# BRACKET_OPEN
	# BRACKET_CLOSE
	# PAREN_OPEN
	# PAREN_CLOSE
	# NEWLINE
	# SPACE
	# TEXT
	# SYMBOL
	
	markdown_token_defs = [
		# ---------------------------------------------
		# 行レベル構文
		# ---------------------------------------------
		{
			"type": "META",					 # --key:value
			"regex": r"^--[^\n]*",
		},
		{
			"type": "TABLE_START",			  # \table
			"regex": r"^\\table[ \t]*\n?",
		},
		{
			"type": "TABLE_ROW",				# | a | b |
			"regex": r"^\|.*\|[ \t]*\n?",
		},
		{
			"type": "HASH",					 # 見出し行の # , ##, ### ...
			"regex": r"^#{1,6}",
		},
		# ---------------------------------------------
		# インライン強調（** と __ は開始と終了どちらでも同じトークン）
		# parser 側で「強調のネスト状態」で判定する
		# ---------------------------------------------
		{
			"type": "BOLD_MARK",				# ** 
			"regex": r"\*\*",
		},
		{
			"type": "ITALIC_MARK",			  # __
			"regex": r"__",
		},
		# ---------------------------------------------
		# リンク構文（内部テキストは TEXT として扱う）
		# ---------------------------------------------
		{
			"type": "BRACKET_OPEN",			 # [
			"regex": r"\[",
		},
		{
			"type": "BRACKET_CLOSE",			# ]
			"regex": r"\]",
		},
		{
			"type": "PAREN_OPEN",			   # (
			"regex": r"\(",
		},
		{
			"type": "PAREN_CLOSE",			  # )
			"regex": r"\)",
		},
		# ---------------------------------------------
		# その他
		# ---------------------------------------------
		{
			"type": "NEWLINE",
			"regex": r"\n+",
		},
		{
			"type": "SPACE",
			"regex": r"[ \t]+",
			"ignore": False,					 # ←重要！元テキスト保持のため無視しない
		},
		{
			"type": "TEXT",					  # どの記号にもマッチしないテキスト
			"regex": r"[^ \t\n\[\]\(\)\*_\\|]+",
		},
		{
			"type": "SYMBOL",					# 最後の砦（1文字）
			"regex": r".",
		},
	]
	
	# レクサーの作成と実行
	lexer = BaseLexer(arg_text, markdown_token_defs)
	tokens = lexer.tokenize()
	
	return tokens
