#  file algorithms/mst.py
import heapq

# --- 1. PRIM ALGORITHM ---
def prim_algorithm(model, start_id):
    """
    Trả về danh sách các cạnh (Edge Objects) thuộc cây khung nhỏ nhất (MST)
    """
    if start_id not in model.vertices:
        return []

    mst_edges = []
    visited = set([start_id])

    # Hàng đợi ưu tiên lưu (trọng số, id_đỉnh_nguồn, id_đỉnh_đích)
    # Lấy tất cả cạnh từ đỉnh bắt đầu
    edges_heap = []
    for edge in model.edges:
        u, v = edge.start_vertex.id, edge.end_vertex.id
        w = edge.weight if edge.weight is not None else 1

        if u == start_id:
            heapq.heappush(edges_heap, (w, u, v, edge))
        elif not model.is_directed and v == start_id:
            heapq.heappush(edges_heap, (w, v, u, edge))

    while edges_heap:
        w, u, v, edge_obj = heapq.heappop(edges_heap)

        if v not in visited:
            visited.add(v)
            mst_edges.append(edge_obj)

            # Thêm các cạnh nối từ đỉnh v mới thăm vào heap
            for next_edge in model.edges:
                nu, nv = next_edge.start_vertex.id, next_edge.end_vertex.id
                nw = next_edge.weight if next_edge.weight is not None else 1

                if nu == v and nv not in visited:
                    heapq.heappush(edges_heap, (nw, nu, nv, next_edge))
                elif not model.is_directed and nv == v and nu not in visited:
                    heapq.heappush(edges_heap, (nw, nv, nu, next_edge))

    return mst_edges

# --- 2. KRUSKAL ALGORITHM ---
def kruskal_algorithm(model):
    """
    Trả về danh sách các cạnh thuộc MST.
    """
    # Sắp xếp tất cả cạnh theo trọng số tăng dần
    sorted_edges = sorted(model.edges, key=lambda e: e.weight if e.weight is not None else 1)

    mst_edges = []

    # Cấu trúc Union-Find để kiểm tra chu trình
    parent = {v_id: v_id for v_id in model.vertices}

    def find_root(node):
        if parent[node] != node:
            parent[node] = find_root(parent[node])
        return parent[node]

    def union(node_a, node_b):
        root_a = find_root(node_a)
        root_b = find_root(node_b)
        if root_a != root_b:
            parent[root_b] = root_a
            return True # Nối thành công (không tạo chu trình)
        return False # Đã nối rồi (tạo chu trình)

    for edge in sorted_edges:
        u, v = edge.start_vertex.id, edge.end_vertex.id
        # Nếu nối u và v không tạo chu trình -> Thêm vào MST
        if union(u, v):
            mst_edges.append(edge)

    return mst_edges
