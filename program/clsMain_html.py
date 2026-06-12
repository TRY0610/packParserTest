#from packParser import clsTest 
#from packParser import clsFileManager
import packParser

class clsMain:
	def __init__(self):
		print("開始")
		#cls = clsTest()
		
		self.cls_FMng = packParser.clsFileManager()
		
		# 設定情報読み込み
		#self.config = self.cls_FMng.readFileJson(con.CONFIG_FILE_PATH)
		
	
	def main(self,arg_text):
		print("解析文字------------------------")
		print("--------------------------------")
		print(arg_text)
		
		print("字句解析------------------------")
		print("--------------------------------")
		tokens = packParser.executeMarkdownLexer(arg_text)
		print(tokens)
		
		print("構文解析------------------------")
		print("--------------------------------")
		parser = packParser.MarkdownParser(tokens)
		ast = parser.parse()
		print(ast)
		
		print("HTML作成------------------------")
		print("--------------------------------")
		renderer = packParser.RendererHTML()
		html = renderer.render(ast)
		print(html)
		#parser = packParser.MarkdownParser(tokens)
		#ast = parser.parse()
		
		print("markdown複製------------------------")
		print("--------------------------------")
		renderer = packParser.RendererMarkdown()
		html = renderer.render(ast)
		print(html)
		
		#Markdoun → Lexer → Parser → AST → Analyzer → Visitor → HTML変換 を