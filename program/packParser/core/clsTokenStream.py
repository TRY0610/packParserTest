class TokenStream:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0

	def peek(self):
		return self.tokens[self.pos]

	def consume(self):
		tok = self.tokens[self.pos]
		self.pos += 1
		return tok

	def match(self, type):
		tok = self.peek()
		if tok.type == type:
			self.consume()
			return tok
		return None

	def expect(self, type):
		tok = self.peek()
		if tok.type != type:
			raise Exception(f"Expected {type}, but got {tok.type}")
		return self.consume()

	def is_end(self):
		return self.peek().type == "EOF"
