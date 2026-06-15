from ..core.baseclsLexer import BaseLexer

def executeJavaLexer(arg_text):
	# 字句の基点となる正規表現一覧
	# 上から順番に判定
	# 
	# キー説明
	# "type": 字句のタイプ
	# "regex": 正規表現
	# "ignore": 無視を行うか(True=無視)
	#
	# 字句タイプ一覧
	
	markdown_token_defs = [
		# ---------------------------------------------
		# キーワード
		# ---------------------------------------------
		{
			"type": "CLASS",            # class
			"regex": r"class\b",
		},
		{
			"type": "SWITCH",           # switch
			"regex": r"switch\b",
		},
		{
			"type": "CASE",             # case
			"regex": r"case\b",
		},
		{
			"type": "DEFAULT",          # default
			"regex": r"default\b",
		},
		{
			"type": "FOR",              # for
			"regex": r"for\b",
		},
		{
			"type": "WHILE",            # while
			"regex": r"while\b",
		},
		{
			"type": "IF",               # if
			"regex": r"if\b",
		},
		{
			"type": "ELSE",             # else
			"regex": r"else\b",
		},
		{
			"type": "COMMENT",          # コメント
			"regex": r"//",
		},
		{
			"type": "COMMENT_MULTI_LINE_OPEN",			 # 複数行コメント開始
			"regex": r"/\*",
		},
		{
			"type": "COMMENT_MULTI_LINE_CLOSE",			 # 複数行コメント終了
			"regex": r"\*/",
		},
		# ---------------------------------------------
		# 括弧
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
		{
			"type": "BRACES_OPEN",			  # {
			"regex": r"\{",
		},
		{
			"type": "BRACES_CLOSE",			  # }
			"regex": r"\}",
		},
		# ---------------------------------------------
		# その他
		# ---------------------------------------------
		{
			"type": "SEMICOLON",
			"regex": r";",
		},
		{
			"type": "COLON",
			"regex": r":",
		},
		{
			"type": "NEWLINE",
			"regex": r"\n+",
		},
		{
			"type": "SPACE",
			"regex": r"[ \t]+",
			"ignore": False,
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
