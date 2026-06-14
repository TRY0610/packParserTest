class RendererMermaid:
    def __init__(self):
        # ファイル（クラス）全体で絶対に重複させないためのノードカウンター
        self.node_count = 0
        self.lines = []

    def render(self, node):
        """レンダリングの開始点 (ClassNodeを想定)"""
        self.lines = []
        self.lines.append("graph TD")
        
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self.render_node(child)
            
        return "\n".join(self.lines)

    def render_node(self, node):
        """ノードの型に応じて適切なメソッドを動的に呼び出す"""
        if node is None:
            return None
        method_name = f"render_{node.__class__.__name__}"
        method = getattr(self, method_name, self.generic_render)
        return method(node)

    def generic_render(self, node):
        # 想定外のノードや、StatementNodeなどは図を描画しないためNoneを返す
        return None

    # ---------------------------------------------------
    # 各ノードのレンダリング処理
    # ---------------------------------------------------

    def render_ClassNode(self, node):
        for child in node.children:
            self.render_node(child)

    def render_FunctionNode(self, node):
        """メソッド（関数）ごとにサブグラフ（枠）を作成する"""
        safe_name = node.name.replace("[", "").replace("]", "").replace('"', "'").strip()
        self.lines.append(f"\n    subgraph \"{safe_name}\"")
        self.lines.append("        direction TD")
        
        # 開始ノード
        self.node_count += 1
        start_id = f"node{self.node_count}"
        self.lines.append(f'        {start_id}(["開始"])')
        
        # 終了ノード
        self.node_count += 1
        end_id = f"node{self.node_count}"
        
        if node.children:
            # 内部のステートメント群を処理し、最終的な末尾のノードID群を獲得
            last_ids = self.render_statements(node.children, [start_id])
            
            # 生き残ったすべての末尾ノードから終了ノードへ合流させる
            for l_id in last_ids:
                self.lines.append(f'        {l_id} --> {end_id}')
        else:
            self.lines.append(f'        {start_id} --> {end_id}')
            
        self.lines.append(f'        {end_id}(["終了"])')
        self.lines.append("    end")

    def render_CommentNode(self, node):
        """純粋な日本語コメントノードのみを描画"""
        if not node.text:
            return None
            
        self.node_count += 1
        node_id = f"node{self.node_count}"
        
        # 改行が含まれている場合はMermaidの仕様に合わせて<br>に置換
        safe_text = node.text.replace('"', "'").replace("\n", "<br>")
        self.lines.append(f'        {node_id}["{safe_text}"]')
        return [node_id]

    def render_IfNode(self, node):
        """IF文（ひし形）の描画と、True/Falseの条件分岐追跡"""
        self.node_count += 1
        if_id = f"node{self.node_count}"
        
        safe_condition = node.conditions.replace('"', "'").strip()
        self.lines.append(f'        {if_id}{{"{safe_condition}"}}')
        
        branch_end_ids = []
        
        # --- True（Yes）側の処理 ---
        if node.trueChildren:
            true_ends = self.render_statements(node.trueChildren, [if_id], branch_label="-->|Yes|")
            if true_ends:
                branch_end_ids.extend(true_ends)
            else:
                branch_end_ids.append(if_id)
        else:
            branch_end_ids.append(if_id)
        
        # --- False（No）側の処理 ---
        if node.falseChildren:
            # else if のように、子要素が単一の IfNode の場合は直接描画を呼び出す
            if len(node.falseChildren) == 1 and node.falseChildren[0].__class__.__name__ == 'IfNode':
                next_if_node = node.falseChildren[0]
                self.node_count += 1
                next_if_id = f"node{self.node_count}"
                
                # 親の if_id から次の next_if_id へ "No" で繋ぐ
                safe_next_condition = next_if_node.conditions.replace('"', "'").strip()
                self.lines.append(f'        {if_id} -->|No| {next_if_id}{{"{safe_next_condition}"}}')
                
                # ネストされた IfNode の内部を解析
                sub_branch_ends = []
                
                # 次のIfNodeのTrue側
                if next_if_node.trueChildren:
                    t_ends = self.render_statements(next_if_node.trueChildren, [next_if_id], branch_label="-->|Yes|")
                    sub_branch_ends.extend(t_ends if t_ends else [next_if_id])
                else:
                    sub_branch_ends.append(next_if_id)
                    
                # 次のIfNodeのFalse側（さらにelse ifが続くか、通常のelseか）
                if next_if_node.falseChildren:
                    f_ends = self.render_statements(next_if_node.falseChildren, [next_if_id], branch_label="-->|No|")
                    sub_branch_ends.extend(f_ends if f_ends else [next_if_id])
                else:
                    sub_branch_ends.append(next_if_id)
                    
                branch_end_ids.extend(sub_branch_ends)
            else:
                # 通常の else ブロックの場合
                false_ends = self.render_statements(node.falseChildren, [if_id], branch_label="-->|No|")
                if false_ends:
                    branch_end_ids.extend(false_ends)
                else:
                    if if_id not in branch_end_ids:
                        branch_end_ids.append(if_id)
        else:
            if if_id not in branch_end_ids:
                branch_end_ids.append(if_id)
                
        # 【重要】render_node(statement) を呼び出した側に「ひし形自体のID」と「分岐の末尾IDリスト」を両方伝える
        # 呼び出し元の構造に合わせて、タプル (自身のID, [末尾のID群]) として返却します
        return (if_id, branch_end_ids)

    # ---------------------------------------------------
    # 矢印を自動でつなぐための補助ロジック
    # ---------------------------------------------------
    def render_statements(self, statements, incoming_ids, branch_label="-->"):
        """
        複数のステートメントを順番に描画し、上から下へ自動で矢印（-->）を繋ぐ。
        """
        active_parent_ids = list(incoming_ids)
        has_connected_first = False
        
        for statement in statements:
            result = self.render_node(statement)
            
            # 表示対象外のノード（None）だった場合は、スキップして以前の有効なノードを維持する
            if not result:
                continue
                
            # IfNode の場合は (if_id, branch_end_ids) のタプルが返ってくるので分解する
            if isinstance(result, tuple):
                current_node_id = result[0]      # ひし形自体のID (直前ノードからここに繋ぎたい)
                next_parent_ids = result[1]      # IF文全体の末尾IDリスト (次のノードへの親になる)
                current_ids = [current_node_id]  # 今回接続ターゲットにするのはひし形ノード
            else:
                # CommentNode などの通常ノードの場合はリストが返ってくる
                current_ids = result
                next_parent_ids = result
                
            # 直前の有効な親ノードが存在すれば、現在のノードへと矢印を引く
            if active_parent_ids:
                label = branch_label if not has_connected_first else "-->"
                for p_id in active_parent_ids:
                    for c_id in current_ids:
                        self.lines.append(f'        {p_id} {label} {c_id}')
            
            # 次のループに向けて有効な親IDを更新
            active_parent_ids = next_parent_ids
            has_connected_first = True
                
        return active_parent_ids
    
    def render_LoopNode(self, node):
        """FOR/WHILE ループ文（ひし形と逆向き矢印）の描画"""
        self.node_count += 1
        loop_id = f"node{self.node_count}"
        
        # 表示用テキスト (例: "while (i < 10)" や "for (int i=0...)" )
        prefix = "for" if node.loop_type == "FOR" else "while"
        safe_condition = f"{prefix} ({node.conditions})".replace('"', "'").strip()
        
        # ループ判定ノード（ひし形）の配置
        self.lines.append(f'        {loop_id}{{"{safe_condition}"}}')
        
        if node.children:
            # ループ内処理の描画（条件ノードから "Yes" で入る）
            loop_ends = self.render_statements(node.children, [loop_id], branch_label="-->|Yes|")
            
            # ループ内処理のすべての末尾から、再び条件判定ノードへ矢印を戻す
            for e_id in loop_ends:
                self.lines.append(f'        {e_id} --> {loop_id}')
                
        # 呼び出し元(render_statements)には、
        # 「このループ自体の侵入口(loop_id)」と「ループ終了後に次に進むポイント([loop_id])」を返す
        # ※ ループ条件が False (No) の時にループを抜けるため、次の親ノードは loop_id 自身になる
        return (loop_id, [loop_id])