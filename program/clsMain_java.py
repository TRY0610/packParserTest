#from packParser import clsTest 
#from packParser import clsFileManager
import packParser.java as packParser

class clsMain:
	def __init__(self):
		self.cls_FMng = packParser.clsFileManager()
	
	def main(self, arg_text):
		tokens = packParser.executeJavaLexer(arg_text)
		parser = packParser.JavaParser(tokens)
		ast = parser.parse()
		renderer = packParser.RendererMermaid()
		mermaid = renderer.render(ast)
		print(mermaid)
		return mermaid
		#parser = packParser.MarkdownParser(tokens)
		#ast = parser.parse()
		"""
		print("markdown複製------------------------")
		print("--------------------------------")
		renderer = packParser.RendererMarkdown()
		html = renderer.render(ast)
		print(html)
		"""
		
		#Markdoun → Lexer → Parser → AST → Analyzer → Visitor → HTML変換 を