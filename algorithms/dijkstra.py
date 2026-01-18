# file algorithms/dijkstra.py
import heapq

def dijkstra_search(graph_model, start_id, end_id):
    """
    Tìm đường đi ngắn nhất từ start_id đến end_id.
    """
    # 1. Khởi tạo
    # Dùng dictionary để lưu khoảng cách
    distances = {v_id: float('inf') for v_id in graph_model.vertices}
    previous = {v_id: None for v_id in graph_model.vertices}
    distances[start_id] = 0

    # Priority Queue: (khoảng_cách, id_đỉnh)
    pq = [(0, start_id)]

    while pq:
        current_dist, current_u = heapq.heappop(pq)

        # Nếu đã đến đích thì dừng
        if current_u == end_id:
            break

        if current_dist > distances[current_u]:
            continue

        # Duyệt qua các cạnh để tìm hàng xóm
        for edge in graph_model.edges:
            neighbor = None

            # --- FIX LỖI TẠI ĐÂY: Đảm bảo trọng số luôn là số nguyên ---
            try:
                w_str = edge.weight if edge.weight is not None else 1
                weight = int(w_str)
            except ValueError:
                weight = 1 # Nếu lỗi thì mặc định là 1
            # -----------------------------------------------------------

            # Kiểm tra xem cạnh này có nối với current_u không
            if edge.start_vertex.id == current_u:
                neighbor = edge.end_vertex.id
            elif not graph_model.is_directed and edge.end_vertex.id == current_u:
                neighbor = edge.start_vertex.id

            if neighbor is not None:
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_u
                    heapq.heappush(pq, (new_dist, neighbor))

    # 2. Truy vết lại đường đi
    path = []
    current = end_id

    # Nếu không tìm thấy đường đi (vẫn là vô cực)
    if distances[end_id] == float('inf'):
        return float('inf'), []

    while current is not None:
        path.insert(0, current)
        current = previous[current]

    return distances[end_id], path
