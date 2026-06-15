import clsMain_java

text = '''
public void printHello() {
    //初期処理
    System.out.println("こんにちは！");
    //ログイン確認
    /*
    こんな処理で
    あんな処理もある
    */
    if (true){
        //こんな処理
        System.out.println("こんな処理！");
        //こんな処理
        System.out.println("こんな処理！");
        System.out.println("こんな処理！");
        System.out.println("こんな処理！");
        //こんな処理
    }else if(add().id){
        //あんな処理
        System.out.println("あんな処理！");
    }else{
        //あんな処理
        System.out.println("あんな処理！");
    }
}
public void printHello2() {
    //初期処理
    System.out.println("こんにちは！");
    //ログイン確認
    for (int i=0;i<10;i++){
        //画面起動
        //こんな処理
        if (a==b){
            //これはこう
        }
    }
}
'''

clsMain = clsMain_java.clsMain()
clsMain.main(text)
