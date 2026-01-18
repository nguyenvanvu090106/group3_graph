# file algorithms/hierholzer.py
import copy

def hierholzer_algorithm(model, start_id):
    """
    Tìm chu trình/đường đi Euler (Hierholzer).
    Xử lý chính xác cả 2 trường hợp: Có hướng (Directed) và Vô hướng (Undirected).
    """
    # ==========================================
    # TRƯỜNG HỢP 1: ĐỒ THỊ VÔ HƯỚNG (UNDIRECTED)
    # ==========================================
    if not model.is_directed:
        adj = {v.id: [] for v in model.vertices.values()}
        degrees = {v.id: 0 for v in model.vertices.values()}

        for edge in model.edges:
            u, v = edge.start_vertex.id, edge.end_vertex.id
            adj[u].append(v); adj[v].append(u)
            degrees[u] += 1; degrees[v] += 1

        odd_nodes = [v for v, d in degrees.items() if d % 2 != 0]

        if len(odd_nodes) not in [0, 2]: return False, []

        # Xử lý đường đi Euler (2 đỉnh lẻ) -> Thêm cạnh ảo
        is_path = (len(odd_nodes) == 2)
        u_odd, v_odd = None, None

        # Lưu lại đỉnh người dùng muốn bắt đầu
        user_requested_start = start_id

        if is_path:
            u_odd, v_odd = odd_nodes[0], odd_nodes[1]
            adj[u_odd].append(v_odd); adj[v_odd].append(u_odd)
            # Nếu user click vào đỉnh chẵn, thuật toán tự chọn đỉnh lẻ
            if start_id not in odd_nodes: start_id = u_odd

        # Chạy thuật toán
        curr_path = [start_id]; circuit = []
        while curr_path:
            curr_v = curr_path[-1]
            if adj[curr_v]:
                next_v = adj[curr_v].pop()
                if curr_v in adj[next_v]: adj[next_v].remove(curr_v)
                curr_path.append(next_v)
            else:
                circuit.append(curr_path.pop())

        circuit = circuit[::-1]

        # Cắt cạnh ảo nếu là đường đi
        if is_path and len(circuit) > 1:
            for i in range(len(circuit) - 1):
                u, v = circuit[i], circuit[i+1]
                if (u == u_odd and v == v_odd) or (u == v_odd and v == u_odd):
                    circuit = circuit[i+1:] + circuit[1:i+1]
                    break

        # [FIX QUAN TRỌNG] Nếu là đường đi Vô Hướng, và kết quả đang bị ngược so với ý user
        # Ví dụ: User chọn 2, kết quả ra 3->1->2. Ta đảo lại thành 2->1->3
        if is_path and circuit:
            if circuit[0] != user_requested_start and circuit[-1] == user_requested_start:
                circuit = circuit[::-1]

        return True, circuit

    # ==========================================
    # TRƯỜNG HỢP 2: ĐỒ THỊ CÓ HƯỚNG (DIRECTED)
    # ==========================================
    else:
        adj = {v.id: [] for v in model.vertices.values()}
        in_degree = {v.id: 0 for v in model.vertices.values()}
        out_degree = {v.id: 0 for v in model.vertices.values()}

        for edge in model.edges:
            u, v = edge.start_vertex.id, edge.end_vertex.id
            adj[u].append(v)
            out_degree[u] += 1; in_degree[v] += 1

        start_nodes = [v for v in adj if out_degree[v] - in_degree[v] == 1]
        end_nodes = [v for v in adj if in_degree[v] - out_degree[v] == 1]

        is_cycle = (len(start_nodes) == 0 and len(end_nodes) == 0)
        is_path = (len(start_nodes) == 1 and len(end_nodes) == 1)

        if not (is_cycle or is_path): return False, []

        unbalanced = [v for v in adj if in_degree[v] != out_degree[v]]
        if is_cycle and len(unbalanced) > 0: return False, []
        if is_path and len(unbalanced) > 2: return False, []

        u_start, v_end = None, None
        if is_path:
            u_start = start_nodes[0]
            v_end = end_nodes[0]
            adj[v_end].append(u_start)
            start_id = u_start
        else:
            if out_degree[start_id] == 0:
                candidates = [v for v in adj if out_degree[v] > 0]
                if candidates: start_id = candidates[0]

        curr_path = [start_id]; circuit = []
        while curr_path:
            curr_v = curr_path[-1]
            if adj[curr_v]:
                next_v = adj[curr_v].pop()
                curr_path.append(next_v)
            else:
                circuit.append(curr_path.pop())

        circuit = circuit[::-1]

        if is_path and len(circuit) > 1:
            for i in range(len(circuit) - 1):
                u, v = circuit[i], circuit[i+1]
                if u == v_end and v == u_start:
                    circuit = circuit[i+1:] + circuit[1:i+1]
                    break

        return True, circuit
