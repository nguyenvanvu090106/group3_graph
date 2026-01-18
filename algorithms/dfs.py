# file algorithms/dfs.py
def dfs_traversal(graph_model, start_id):
    """
    Duyệt DFS (Dùng Stack). Trả về: (traversal_order, traversal_edges)
    """
    visited = set()
    stack = [start_id]

    traversal_order = []
    traversal_edges = []

    # Để truy vết cạnh nào dẫn đến đỉnh nào, ta dùng dictionary cha-con
    parent_map = {start_id: None}

    while stack:
        u_id = stack.pop()

        if u_id not in visited:
            visited.add(u_id)
            traversal_order.append(u_id)

            # Nếu đỉnh này có cha (không phải đỉnh đầu), tìm cạnh nối cha-con để tô màu
            p_id = parent_map[u_id]
            if p_id is not None:
                # Tìm cạnh nối giữa p_id và u_id
                for edge in graph_model.edges:
                    is_direct = (edge.start_vertex.id == p_id and edge.end_vertex.id == u_id)
                    is_undirect = (not graph_model.is_directed and edge.start_vertex.id == u_id and edge.end_vertex.id == p_id)
                    if is_direct or is_undirect:
                        traversal_edges.append(edge)
                        break

            # Lấy hàng xóm
            neighbors = []
            for edge in graph_model.edges:
                neighbor_id = None
                if edge.start_vertex.id == u_id:
                    neighbor_id = edge.end_vertex.id
                elif not graph_model.is_directed and edge.end_vertex.id == u_id:
                    neighbor_id = edge.start_vertex.id

                if neighbor_id is not None and neighbor_id not in visited:
                    neighbors.append(neighbor_id)

            # Sắp xếp giảm dần vì Stack lấy ra sẽ là phần tử cuối cùng (ID nhỏ nhất sẽ được lấy ra trước)
            neighbors.sort(reverse=True)

            for v_id in neighbors:
                if v_id not in visited:
                    stack.append(v_id)
                    parent_map[v_id] = u_id # Ghi nhận cha của v là u

    return traversal_order, traversal_edges
