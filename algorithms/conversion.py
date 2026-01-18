# file algorithms/conversion.py

def get_adjacency_matrix(model):
    """Chuyển đổi sang Ma trận kề (Adjacency Matrix)"""
    # 1. Lấy danh sách ID các đỉnh và sắp xếp để ma trận đẹp
    vertex_ids = sorted(model.vertices.keys())
    n = len(vertex_ids)

    # 2. Tạo map để biết đỉnh ID nào ứng với chỉ số hàng/cột nào (0, 1, 2...)
    # Ví dụ: Đỉnh ID=5 ứng với index=0, ID=9 ứng với index=1
    id_to_index = {v_id: i for i, v_id in enumerate(vertex_ids)}

    # 3. Khởi tạo ma trận n x n toàn số 0
    matrix = [[0] * n for _ in range(n)]

    # 4. Điền trọng số vào ma trận
    for edge in model.edges:
        u = edge.start_vertex.id
        v = edge.end_vertex.id
        weight = edge.weight if edge.weight is not None else 1

        # Lấy index trong ma trận
        i = id_to_index[u]
        j = id_to_index[v]

        matrix[i][j] = weight

        # Nếu là vô hướng thì điền cả chiều ngược lại
        if not model.is_directed:
            matrix[j][i] = weight

    # 5. Chuyển thành String đẹp để hiển thị
    # Header (Tên các đỉnh)
    labels = [str(model.vertices[vid].label) for vid in vertex_ids]
    header = "      " + "  ".join(f"{lbl:>4}" for lbl in labels)

    rows = []
    for i in range(n):
        row_label = labels[i]
        row_data = "  ".join(f"{val:>4}" for val in matrix[i])
        rows.append(f"{row_label:>4} | {row_data}")

    return header + "\n" + ("-" * len(header)) + "\n" + "\n".join(rows)

def get_adjacency_list(model):
    """Chuyển đổi sang Danh sách kề (Adjacency List)"""
    adj_list = {v_id: [] for v_id in model.vertices}

    for edge in model.edges:
        u = edge.start_vertex.id
        v = edge.end_vertex.id
        w = edge.weight if edge.weight is not None else 1

        # Thêm vào danh sách của u
        adj_list[u].append(f"{model.vertices[v].label}(w={w})")

        # Nếu vô hướng, thêm vào danh sách của v
        if not model.is_directed:
            adj_list[v].append(f"{model.vertices[u].label}(w={w})")

    # Tạo string kết quả
    lines = []
    for v_id in sorted(adj_list.keys()):
        label = model.vertices[v_id].label
        neighbors = ", ".join(adj_list[v_id])
        lines.append(f"{label} -> [{neighbors}]")

    return "\n".join(lines)

def get_edge_list(model):
    """Chuyển đổi sang Danh sách cạnh (Edge List)"""
    lines = []
    # Header
    lines.append(f"{'Start':<10} {'End':<10} {'Weight':<10}")
    lines.append("-" * 35)

    for edge in model.edges:
        u_lbl = edge.start_vertex.label
        v_lbl = edge.end_vertex.label
        w = edge.weight if edge.weight is not None else 1

        lines.append(f"{str(u_lbl):<10} {str(v_lbl):<10} {str(w):<10}")

        # Lưu ý: Với danh sách cạnh, thường người ta liệt kê đúng số cạnh thực tế.
        # Nếu vô hướng, 1 cạnh vẽ ra chỉ tính là 1 dòng (dù logic là 2 chiều).

    return "\n".join(lines)
