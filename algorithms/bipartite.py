# file algorithms/bipartite.py
from collections import deque

def check_bipartite(graph_model):
    """
    Kiểm tra đồ thị 2 phía (Bipartite Graph) bằng thuật toán tô màu (BFS).
    Quy tắc: Đỉnh kề nhau phải khác màu (0 vs 1).

    Trả về:
        - Kết quả (True/False)
        - Dictionary màu {vertex_id: 0 hoặc 1} để vẽ lên giao diện.
    """
    color_map = {} # Lưu trạng thái màu: {id: 0/1}

    # Duyệt qua tất cả các đỉnh (đề phòng đồ thị bị ngắt quãng - disconnected components)
    for start_node_id in graph_model.vertices:
        if start_node_id not in color_map:
            # Gán màu đầu tiên là 0 (Xanh)
            color_map[start_node_id] = 0
            queue = deque([start_node_id])

            while queue:
                u_id = queue.popleft()
                current_color = color_map[u_id]
                next_color = 1 - current_color # Đảo màu: 0->1, 1->0

                # Lấy danh sách hàng xóm (xét như vô hướng để kiểm tra cấu trúc)
                neighbors = []
                for edge in graph_model.edges:
                    neighbor = None
                    if edge.start_vertex.id == u_id:
                        neighbor = edge.end_vertex.id
                    elif edge.end_vertex.id == u_id:
                        neighbor = edge.start_vertex.id

                    if neighbor is not None:
                        neighbors.append(neighbor)

                # Kiểm tra màu các hàng xóm
                for v_id in neighbors:
                    if v_id not in color_map:
                        # Chưa có màu -> Tô màu ngược lại và đẩy vào hàng đợi
                        color_map[v_id] = next_color
                        queue.append(v_id)
                    elif color_map[v_id] == current_color:
                        # Đã có màu mà lại TRÙNG màu với u -> Mâu thuẫn -> Không phải 2 phía
                        return False, {}

    return True, color_map
