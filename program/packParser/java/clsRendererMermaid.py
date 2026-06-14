class RendererMermaid:
    def __init__(self):
        self.node_count = 0
        self.lines = []

    def render(self, node):
        """レンダリングの開始点 (ClassNodeを想定)"""
        self.lines = []
        self.lines.append("graph TD")
        
        # クラス内の子ノード（各FunctionNode）を処理
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
        raise NotImplementedError(f"No render method for {node.__class__.__name__}")

    # ---------------------------------------------------
    # 各ノードのレンダリング処理
    # ---------------------------------------------------

    def render_ClassNode(self, node):
        for child in node.children:
            self.render_node(child)

    def render_FunctionNode(self, node):
        """メソッド（関数）ごとにサブグラフ（枠）を作成する"""
        self.node_count = 0
        
        # 関数名に含まれる可能性のある不適切な文字を削除・エスケープ
        safe_name = node.name.replace("[", "").replace("]", "").replace('"', '\\"').strip()
        
        self.lines.append(f"\n    subgraph \"{safe_name}\"")
        
        if node.children:
            self.render_statements(node.children)
            
        self.lines.append("    end")

    def render_CommentNode(self, node):
        """通常の処理文やコメントを四角い箱として定義し、そのIDを返す"""
        self.node_count += 1
        node_id = f"node{self.node_count}"
        
        # node.text から安全に文字列を取得してエスケープ
        raw_text = getattr(node, 'text', '')
        if not raw_text:
            raw_text = getattr(node, 'children', '（空の処理）')
            
        safe_text = str(raw_text).replace('"', '\\"').strip()
        
        # Mermaid定義: node1["コメント内容"]
        self.lines.append(f'        {node_id}["{safe_text}"]')
        return [node_id]

    def render_IfNode(self, node):
        """IF文（ひし形）の描画と、True/Falseの分岐の接続を行う"""
        self.node_count += 1
        if_id = f"node{self.node_count}"
        
        safe_condition = node.conditions.replace('"', '\\"').strip()
        self.lines.append(f'        {if_id}{{{safe_condition}}}')
        
        # --- True（Yes）側の処理 ---
        if node.trueChildren:
            true_ids = self.render_statements(node.trueChildren)
            if true_ids:
                self.lines.append(f'        {if_id} -->|Yes| {true_ids[0]}')
        
        # --- False（No）側の処理 ---
        if node.falseChildren:
            false_ids = self.render_statements(node.falseChildren)
            if false_ids:
                self.lines.append(f'        {if_id} -->|No| {false_ids[0]}')
                
        return [if_id]

    # ---------------------------------------------------
    # 矢印を自動でつなぐための補助ロジック
    # ---------------------------------------------------
    def render_statements(self, statements):
        """複数のステートメントを順番に描画し、上から下へ自動で矢印（-->）を繋ぐ"""
        previous_ids = []
        first_node_ids = []
        
        for statement in statements:
            current_ids = self.render_node(statement)
            if not current_ids:
                continue
                
            if not first_node_ids:
                first_node_ids = current_ids
                
            if previous_ids:
                for p_id in previous_ids:
                    for c_id in current_ids:
                        self.lines.append(f'        {p_id} --> {c_id}')
                        
            previous_ids = current_ids
            
        return first_node_ids