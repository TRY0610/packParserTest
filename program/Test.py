import clsMain_html

text = '''こんにちは
\\table
|A|B|
|C|D|

**ヤッホー__こんにちは__**
[これはリンクだよ]
[これは外部リンクだよ](http://aiueo)

#タイトル1
##タイトル2
###タイトル3
ここは 空白テスト
'''

clsMain = clsMain_html.clsMain()
clsMain.main(text)
