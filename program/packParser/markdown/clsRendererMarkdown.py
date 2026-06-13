import html

class RendererMarkdown:
	# 連打リング開始
	def render(self, node):
		method_name = f"render_{node.__class__.__name__}"
		method = getattr(self, method_name, self.generic_render)
		return method(node)
	
	# エラーメソッド
	def generic_render(self, node):
		raise NotImplementedError(f"No render method for {node.__class__.__name__}")
	
	#---------------------------------------------------
	
	def render_DocumentNode(self, node):
		return "".join(self.render(child) for child in node.children)
	
	def render_ParagraphNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		return f"{inner}\n"
	
	def render_MetaNode(self, node):
		#メタ情報はHTMLには出力しない(隠し情報として今後出力させるかも？)
		return f"--{node.key}:{node.value}\n"
	
	def render_TextNode(self, node):
		return self.escape_html(node.text)
	
	def escape_html(self, text):
		return html.escape(text)
	
	def render_BoldNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		return f"**{inner}**"
	
	def render_ItalicNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		return f"__{inner}__"
	
	def render_LinkNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		
		if node.url:
			return f'[{inner}]({node.url})'
		else:
			# サイト内リンク or 未解決リンク想定
			return f'[{inner}]'
	
	def render_HeadingNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		return f"{'#' * node.level}{inner}\n"
	
	def render_TableNode(self, node):
		text=[]
		text.append(f"{node.rows}")
		
		return "".join(text)
