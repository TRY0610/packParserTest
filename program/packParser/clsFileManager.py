import shutil
import json
import os


# ファイル操作クラス
class clsFileManager:
	# コンストラクタ
	def __init__(self):
		self.F_file:_io.TextIOWrapper| None = None
	
	# ファイル読み込み(一行ごとにリスト)
	def readFileList(self,argFilePath):
		self._openFile(argFilePath,argMode="r")
		textList=self._getFileStrList()
		self._closeFile()
		return textList
	
	# ファイル読み込み(一括)
	def readFile(self,argFilePath):
		self._openFile(argFilePath,argMode="r")
		text=self._getFileStr()
		self._closeFile()
		return text
	
	# ファイル保存
	def writeFile(self,argFilePath,argText,argMode):
		self._openFile(argFilePath,argMode=argMode)
		result=self._writeFile(argText)
		self._closeFile()
		return result
	
	# 新規書き込み保存
	def writeNewFile(self,argFilePath,argText):
		return self.writeFile(argFilePath,argText,"x")
	
	# 追記書き込み保存
	def writeAddFile(self,argFilePath,argText):
		return self.writeFile(argFilePath,argText,"a")
	
	# 上書き保存
	def writeOverFile(self,argFilePath,argText):
		return self.writeFile(argFilePath,argText,"w")
	
	# ファイル読み込み(JSON)
	def readFileJson(self,argFilePath):
		return json.loads(self.readFile(argFilePath))
	
	# ファイル保存(JSON上書き)
	def writeFileJson(self,argFilePath,argText):
		return self.writeFile(argFilePath,json.dumps(argText, indent=4, sort_keys=True, ensure_ascii=False),"w")
	
	# ファイル移動
	def moveFile(self,argNowPath,argNewPath):
		shutil.move(argNowPath, argNewPath)
	
	# フォルダ作成
	def createDirectory(self,arg_path):
		os.makedirs(arg_path, exist_ok=True)
	
	# ファイル削除
	def deleteFile(self,arg_path):
		os.remove(arg_path)
	
	# ファイル確認
	def checkExist(self,arg_path):
		return os.path.exists(arg_path)
	
	#プライベート---------------------------------------------------
	#内容文字列を取得
	def _getFileStr(self):
		return self.F_file.read()
	
	#内容文字列を一行ごとにリストで取得
	def _getFileStrList(self):
		return self.F_file.readlines()
	
	#ファイルに書き込む(リスト、文字列対応)
	def _writeFile(self,argText):
		if isinstance(argText, str):  # 文字列の場合
			self.F_file.write(argText)
		elif isinstance(argText, list):  # リストの場合
			self.F_file.writelines(argText)
		else:
			raise TypeError("str または list[str] を渡してください")
		return True
	
	'''
	ファイルを開く
	argMode
	r :読取り				←デフォ
	w :書き込み(上書き許可)
	x :書き込み(新規のみ)
	a :追記
	'''
	def _openFile(self,argFilePath,argMode="r",argEncoding="utf-8"):
		self.F_file=open(argFilePath, mode=argMode, encoding=argEncoding)
		return True
	
	#ファイルを閉じる
	def _closeFile(self):
		self.F_file.close()
		self.F_file=None
		return True
		
		
