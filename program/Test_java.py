import clsMain_java

texts =[ '''
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
    }else if(add().id){
        //あんな処理
        System.out.println("あんな処理！");
    }else{
        //そんな処理
        System.out.println("そんな処理！");
    }
    //終了
}
''',
'''
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
''',
'''
public void printHello3() {
    //合格ですを表示
    if (score >= 80) System.out.println("合格です");
    //合格ですを表示完了
}
''',
'''
public void printHello4() {
    int num = 2;
    switch (num) {
        case 1:
            //値は1
            System.out.println("値は1です");
            break;
        case 2:
            //値は2
            System.out.println("値は2です");
            break;
        default:
            //その他
            System.out.println("該当なし");
            break;
    }
}
''',
'''
public void printHello5() {
    //@この値がTRYEの時
    if (true){
        //こんな処理
        System.out.println("こんな処理！");
    //@この場合は
    }else if(add().id){
        //あんな処理
        System.out.println("あんな処理！");
    }else{
        //あんな処理
        System.out.println("あんな処理！");
    }
}
''',
'''
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;
import java.util.stream.IntStream;


public class PracticalExample {

    public static void main(String[] args) {
        // スレッドプールの生成（実務では必須のステップ）
        ExecutorService executor = Executors.newFixedThreadPool(4);

        // 処理対象のデータリスト（例：1〜10のタスク）
        List<Integer> taskIds = IntStream.rangeClosed(1, 10).boxed().toList();

        try {
            // --- 2. 並行処理と非同期処理の組み合わせ ---
            // 各タスクを非同期で実行し、CompletableFutureのリストを作成
            List<CompletableFuture<TaskResult>> futures = taskIds.stream()
                    .map(id -> CompletableFuture.supplyAsync(() -> executeTask(id), executor))
                    .toList();

            // --- 3. Stream APIによるデータ処理・集計 ---
            // 全ての非同期処理が完了するのを待機し、結果をまとめる
            List<TaskResult> results = CompletableFuture.allOf(
                    futures.toArray(new CompletableFuture[0])
            ).thenApply(v ->
                    futures.stream()
                            .map(CompletableFuture::join) // 結果を取り出す
                            .filter(result -> "SUCCESS".equals(result.status())) // フィルタリング
                            .collect(Collectors.toList())
            ).join();

            // --- 4. 結果の出力 ---
            System.out.println("--- 処理成功したタスク一覧 ---");
            results.forEach(System.out::println);

        } finally {
            // スレッドプールのシャットダウン（リソース解放）
            executor.shutdown();
        }
    }

    // --- 実務を模したタスク処理メソッド ---
    private static TaskResult executeTask(int id) {
        System.out.println("タスク " + id + " を実行中... (スレッド: " + Thread.currentThread().getName() + ")");
        long startTime = System.currentTimeMillis();

        try {
            // 擬似的な重い処理（0.5秒〜1.5秒待機）
            Thread.sleep((long) (Math.random() * 1000) + 500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return new TaskResult(id, "INTERRUPTED", 0);
        }

        long duration = System.currentTimeMillis() - startTime;
        return new TaskResult(id, "SUCCESS", duration);
    }
}
'''
]

for text in texts:
    try:
        clsMain = clsMain_java.clsMain()
        clsMain.main(text)
    except Exception as e:
        # エラーメッセージを表示
        print(f"エラーが発生しました: {e}")
