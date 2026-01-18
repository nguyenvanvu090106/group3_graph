# file algorithms/euler.py
import copy

def fleury_algorithm(graph_model, start_id):
    """
    Tìm chu trình Euler (hoặc đường đi Euler).
    Trả về: (Success, Path_of_Vertex_IDs)
    """
    # 1. Kiểm tra điều kiện Euler (bậc chẵn/lẻ)
    degrees = {v: 0 for v in graph_model.vertices}
    adj = {v: [] for v in graph_model.vertices}

    # Xây dựng danh sách kề tạm thời (copy dữ liệu để không hỏng graph chính)
    edges_copy = []

    for edge in graph_model.edges:
        u, v = edge.start_vertex.id, edge.end_vertex.id
        edges_copy.append({'u': u, 'v': v, 'id': id(edge)}) # Dùng ID bộ nhớ để định danh cạnh

        adj[u].append(v)
        degrees[u] += 1
        if not graph_model.is_directed:
            adj[v].append(u)
            degrees[v] += 1

    # Đếm số đỉnh bậc lẻ
    odd_vertices = [v for v, deg in degrees.items() if deg % 2 != 0]

    # Nếu có > 2 đỉnh bậc lẻ -> Không có Euler
    if len(odd_vertices) > 2:
        return False, []

    # Nếu có 2 đỉnh bậc lẻ, phải bắt đầu từ 1 trong 2 đỉnh đó
    if len(odd_vertices) == 2 and start_id not in odd_vertices:
        start_id = odd_vertices[0]

    # 2. Thuật toán Fleury
    # Hàm kiểm tra cầu (Bridge)
    def is_valid_next_edge(u, v, current_adj):
        if len(current_adj[u]) == 1:
            return True # Chỉ còn 1 đường thì bắt buộc phải đi

        # Đếm số đỉnh đến được từ u trước khi xóa cạnh u-v
        visited_before = set()
        stack = [u]
        while stack:
            curr = stack.pop()
            if curr not in visited_before:
                visited_before.add(curr)
                for neighbor in current_adj[curr]:
                    if neighbor not in visited_before:
                        stack.append(neighbor)
        count_before = len(visited_before)

        # Xóa tạm cạnh u-v
        current_adj[u].remove(v)
        if not graph_model.is_directed:
            current_adj[v].remove(u)

        # Đếm số đỉnh đến được sau khi xóa
        visited_after = set()
        stack = [u]
        while stack:
            curr = stack.pop()
            if curr not in visited_after:
                visited_after.add(curr)
                for neighbor in current_adj[curr]:
                    if neighbor not in visited_after:
                        stack.append(neighbor)
        count_after = len(visited_after)

        # Hoàn trả lại cạnh
        current_adj[u].append(v)
        if not graph_model.is_directed:
            current_adj[v].append(u)

        return count_before == count_after # Nếu số đỉnh đến được giảm -> Là cầu -> False

    # Bắt đầu đi
    path = [start_id]
    curr = start_id

    # Số cạnh cần đi
    total_edges = len(edges_copy)

    while len(path) <= total_edges:
        if not adj[curr]: break

        found_edge = False
        for neighbor in adj[curr]:
            if is_valid_next_edge(curr, neighbor, adj):
                # Chọn cạnh này
                adj[curr].remove(neighbor)
                if not graph_model.is_directed:
                    adj[neighbor].remove(curr)

                path.append(neighbor)
                curr = neighbor
                found_edge = True
                break

        if not found_edge: # Trường hợp kẹt (chỉ còn cầu để đi)
             if adj[curr]:
                neighbor = adj[curr][0]
                adj[curr].remove(neighbor)
                if not graph_model.is_directed:
                    adj[neighbor].remove(curr)
                path.append(neighbor)
                curr = neighbor

    return True, path
