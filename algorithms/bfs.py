#  file algorithms/bfs.py
from collections import deque

def bfs_traversal(graph_model, start_id):
    """
    Duyệt BFS. Trả về: (traversal_order, traversal_edges)
    - traversal_order: Danh sách ID các đỉnh đã duyệt.
    - traversal_edges: Danh sách các cạnh (Object Edge) đã đi qua.
    """
    visited = set()
    queue = deque([start_id])
    visited.add(start_id)

    traversal_order = [start_id]
    traversal_edges = []

    while queue:
        u_id = queue.popleft()

        # Lấy danh sách kề và sắp xếp theo ID để kết quả nhất quán
        neighbors = []
        # Tìm các cạnh nối với u_id
        connected_edges = []

        for edge in graph_model.edges:
            neighbor_id = None
            if edge.start_vertex.id == u_id:
                neighbor_id = edge.end_vertex.id
            elif not graph_model.is_directed and edge.end_vertex.id == u_id:
                neighbor_id = edge.start_vertex.id

            if neighbor_id is not None:
                neighbors.append((neighbor_id, edge))

        # Sắp xếp theo ID đỉnh hàng xóm (bé trước lớn sau)
        neighbors.sort(key=lambda x: x[0])

        for v_id, edge_obj in neighbors:
            if v_id not in visited:
                visited.add(v_id)
                queue.append(v_id)
                traversal_order.append(v_id)
                traversal_edges.append(edge_obj) # Lưu lại cạnh này để tô màu

    return traversal_order, traversal_edges
