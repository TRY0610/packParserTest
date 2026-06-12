from .baseclsLexer import BaseLexer


def executeSqlLexer(arg_text):
	markdown_token_defs = [
		{"type": "BOLD",   "regex": r"^\*\*"},#**
		{"type": "ITALIC", "regex": r"^\*"},#
		{"type": "NEWLINE", "regex": r"^\n"},
		{"type": "TEXT",   "regex": r"^[^*\n]+"},
	]
	
	lexer = BaseLexer(arg_text, markdown_token_defs)
	tokens = lexer.tokenize()
	print(tokens)
