# file algorithms/max_flow.py
from collections import deque

def bfs_find_path(graph_adj, source, sink, parent):
    """Hàm tìm đường tăng luồng bằng BFS"""
    visited = set()
    queue = deque([source])
    visited.add(source)
    parent[source] = -1

    while queue:
        u = queue.popleft()
        for v in graph_adj[u]:
            # Nếu chưa thăm và còn dung lượng dư (residual capacity > 0)
            if v not in visited and graph_adj[u][v] > 0:
                queue.append(v)
                visited.add(v)
                parent[v] = u
                if v == sink:
                    return True
    return False

def ford_fulkerson(model, source_id, sink_id):
    """
    Thuật toán Edmonds-Karp (cài đặt của Ford-Fulkerson).
    Trả về: (max_flow_value, flow_dict)
    """
    # 1. Xây dựng đồ thị thặng dư (Residual Graph)
    # graph_adj[u][v] lưu dung lượng còn lại
    graph_adj = {v: {} for v in model.vertices}

    # Copy trọng số vào đồ thị
    for edge in model.edges:
        u, v = edge.start_vertex.id, edge.end_vertex.id
        cap = edge.weight if edge.weight is not None else 1

        # Cạnh xuôi
        if v not in graph_adj[u]: graph_adj[u][v] = 0
        graph_adj[u][v] += cap

        # Cạnh ngược (khởi tạo bằng 0 nếu là có hướng)
        if u not in graph_adj[v]: graph_adj[v][u] = 0
        if not model.is_directed:
            graph_adj[v][u] += cap

    parent = {}
    max_flow = 0
    flow_on_edges = {} # Lưu lượng thực tế chảy qua cạnh để vẽ

    # 2. Lặp tìm đường tăng luồng
    while bfs_find_path(graph_adj, source_id, sink_id, parent):
        path_flow = float('inf')
        s = sink_id

        # Tìm nút thắt cổ chai (bottleneck) trên đường đi
        while s != source_id:
            path_flow = min(path_flow, graph_adj[parent[s]][s])
            s = parent[s]

        # Cập nhật dung lượng thặng dư
        max_flow += path_flow
        v = sink_id
        while v != source_id:
            u = parent[v]
            graph_adj[u][v] -= path_flow # Giảm chiều xuôi
            graph_adj[v][u] += path_flow # Tăng chiều ngược

            # Lưu lại flow để hiển thị
            edge_key = (u, v)
            if edge_key not in flow_on_edges: flow_on_edges[edge_key] = 0
            flow_on_edges[edge_key] += path_flow

            v = parent[v]

    return max_flow, flow_on_edges
