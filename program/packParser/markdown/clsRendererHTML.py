import html

class RendererHTML:
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
		return f"<p>{inner}</p>\n"
	
	def render_MetaNode(self, node):
		#メタ情報はHTMLには出力しない(隠し情報として今後出力させるかも？)
		return f""
	
	def render_TextNode(self, node):
		return self.escape_html(node.text)
	
	def escape_html(self, text):
		return html.escape(text)
	
	def render_BoldNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		return f"<strong>{inner}</strong>"
	
	def render_ItalicNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		return f"<em>{inner}</em>"
	
	def render_LinkNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		
		if node.url:
			return f'<a href="{self.escape_html(node.url)}">{inner}</a>'
		else:
			# サイト内リンク or 未解決リンク想定
			return f'<a href="#">(未作成){inner}</a>'
	
	def render_HeadingNode(self, node):
		inner = "".join(self.render(child) for child in node.children)
		return f"<h{node.level}>{inner}</h{node.level}>\n"
	
	def render_TableNode(self, node):
		lines = node.rows.splitlines()
	
		rows = []
		for line in lines:
			if line.startswith("|"):
				cells = [c for c in line.split("|")[1:-1]]
				rows.append(cells)
	
		html = ["<table>"]
		for row in rows:
			html.append("<tr>")
			for cell in row:
				html.append(f"<td>{self.escape_html(cell)}</td>")
			html.append("</tr>")
		html.append("</table>\n")
	
		return "".join(html)
