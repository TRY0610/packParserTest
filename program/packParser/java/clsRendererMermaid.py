class RendererMermaid:
    def __init__(self):
        # ファイル（クラス）全体で絶対に重複させないためのノードカウンター
        self.node_count = 0
        self.lines = []
        self.pending_label = None

    def render(self, node):
        """レンダリングの開始点 (ClassNodeを想定)"""
        self.lines = []
        self.pending_label = None
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
        if node.name:
            safe_name = node.name.replace("[", "").replace("]", "").replace('"', "'").strip()
            self.lines.append(f"\n    subgraph \"クラス {safe_name}\"")
            self.lines.append("        direction TD")
            for child in node.children:
                self.render_node(child)
            self.lines.append("    end")
        else:
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

    def render_LabelNode(self, node):
        self.pending_label = node.text.strip()
        return None

    def render_StatementNode(self, node):
        return None

    def render_IfNode(self, node):
        """IF文（ひし形）の描画と、True/Falseの条件分岐追跡"""
        self.node_count += 1
        if_id = f"node{self.node_count}"

        safe_condition = node.conditions.replace('"', "'").strip()
        if self.pending_label:
            safe_label = self.pending_label.replace('"', "'").strip()
            safe_condition = f"{safe_label} ({safe_condition})" if safe_condition else safe_label
            self.pending_label = None
        elif getattr(node, 'label', None):
            safe_condition = f"{node.label} ({safe_condition})" if safe_condition else node.label

        self.lines.append(f'        {if_id}{{"{safe_condition}"}}')

        branch_end_ids = []

        if node.trueChildren:
            true_ends = self.render_statements(node.trueChildren, [if_id], branch_label="-->|Yes|")
            if true_ends:
                branch_end_ids.extend(true_ends)
            else:
                branch_end_ids.append(if_id)
        else:
            branch_end_ids.append(if_id)

        if node.falseChildren:
            if len(node.falseChildren) == 1 and node.falseChildren[0].__class__.__name__ == 'IfNode':
                next_if_node = node.falseChildren[0]
                self.node_count += 1
                next_if_id = f"node{self.node_count}"

                safe_next_condition = next_if_node.conditions.replace('"', "'").strip()
                self.lines.append(f'        {if_id} -->|No| {next_if_id}{{"{safe_next_condition}"}}')

                sub_branch_ends = []
                if next_if_node.trueChildren:
                    t_ends = self.render_statements(next_if_node.trueChildren, [next_if_id], branch_label="-->|Yes|")
                    sub_branch_ends.extend(t_ends if t_ends else [next_if_id])
                else:
                    sub_branch_ends.append(next_if_id)

                if next_if_node.falseChildren:
                    f_ends = self.render_statements(next_if_node.falseChildren, [next_if_id], branch_label="-->|No|")
                    sub_branch_ends.extend(f_ends if f_ends else [next_if_id])
                else:
                    sub_branch_ends.append(next_if_id)

                branch_end_ids.extend(sub_branch_ends)
            else:
                false_ends = self.render_statements(node.falseChildren, [if_id], branch_label="-->|No|")
                if false_ends:
                    branch_end_ids.extend(false_ends)
                else:
                    if if_id not in branch_end_ids:
                        branch_end_ids.append(if_id)
        else:
            if if_id not in branch_end_ids:
                branch_end_ids.append(if_id)

        return (if_id, branch_end_ids)

    def render_SwitchNode(self, node):
        self.node_count += 1
        switch_id = f"node{self.node_count}"

        safe_condition = node.condition.replace('"', "'").strip()
        if self.pending_label:
            safe_label = self.pending_label.replace('"', "'").strip()
            safe_condition = f"{safe_label} ({safe_condition})" if safe_condition else safe_label
            self.pending_label = None
        elif getattr(node, 'label', None):
            safe_condition = f"{node.label} ({safe_condition})" if safe_condition else node.label

        self.lines.append(f'        {switch_id}{{"{safe_condition}"}}')

        branch_end_ids = []
        for case in node.cases:
            case_label = case.label.replace('"', "'").strip() if case.label else ""
            label_text = f"case {case_label}" if case_label else "case"
            ends = self.render_statements(case.children, [switch_id], branch_label=f"-->|{label_text}|")
            branch_end_ids.extend(ends if ends else [switch_id])

        if node.defaultCase:
            ends = self.render_statements(node.defaultCase.children, [switch_id], branch_label="-->|default|")
            branch_end_ids.extend(ends if ends else [switch_id])

        if not node.cases and not node.defaultCase:
            branch_end_ids.append(switch_id)

        return (switch_id, branch_end_ids)

    # ---------------------------------------------------
    # 矢印を自動でつなぐための補助ロジック
    # ---------------------------------------------------
    def render_statements(self, statements, incoming_ids, branch_label="-->"):
        """
        複数のステートメントを順番に描画し、上から下へ自動で矢印（-->）を繋ぐ。
        """
        active_parent_ids = list(incoming_ids)
        has_connected_first = False
        pending_outgoing_label = None

        for statement in statements:
            result = self.render_node(statement)

            if not result:
                continue

            if isinstance(result, tuple):
                current_node_id = result[0]
                next_parent_ids = result[1]
                current_ids = [current_node_id]
                pending_outgoing_label = result[2] if len(result) >= 3 else None
            else:
                current_ids = result
                next_parent_ids = result

            if active_parent_ids:
                if pending_outgoing_label is not None and not has_connected_first:
                    label = pending_outgoing_label
                    pending_outgoing_label = None
                else:
                    label = branch_label if not has_connected_first else "-->"
                for p_id in active_parent_ids:
                    for c_id in current_ids:
                        self.lines.append(f'        {p_id} {label} {c_id}')

            active_parent_ids = next_parent_ids
            has_connected_first = True

        return active_parent_ids

    def render_LoopNode(self, node):
        """FOR/WHILE ループ文（ひし形と逆向き矢印）の描画"""
        self.node_count += 1
        loop_id = f"node{self.node_count}"

        prefix = "for" if node.loop_type == "FOR" else "while"
        safe_condition = f"{prefix} ({node.conditions})".replace('"', "'").strip()
        if self.pending_label:
            safe_label = self.pending_label.replace('"', "'").strip()
            safe_condition = f"{safe_label} ({safe_condition})" if safe_condition else safe_label
            self.pending_label = None

        self.lines.append(f'        {loop_id}{{"{safe_condition}"}}')

        if node.children:
            loop_ends = self.render_statements(node.children, [loop_id], branch_label="-->|Yes|")
            for e_id in loop_ends:
                self.lines.append(f'        {e_id} --> {loop_id}')

        return (loop_id, [loop_id], "-->|No|")