from flask import Flask, render_template, request, jsonify
import sys
import os
import networkx as nx  # Thư viện xử lý đồ thị mạnh mẽ cho Max Flow

# 1. Setup đường dẫn để import được code cũ (nằm cùng thư mục cha)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Import logic cũ (Algorithms & Graph Model)
from graph.graph_model import GraphModel
from algorithms.bfs import bfs_traversal
from algorithms.dfs import dfs_traversal
from algorithms.dijkstra import dijkstra_search
from algorithms.mst import prim_algorithm, kruskal_algorithm
from algorithms.euler import fleury_algorithm
from algorithms.hierholzer import hierholzer_algorithm
from algorithms.bipartite import check_bipartite
from algorithms.conversion import get_adjacency_matrix, get_adjacency_list, get_edge_list

app = Flask(__name__)

# --- HÀM BỔ TRỢ: Tái tạo GraphModel từ JSON gửi lên ---
def rebuild_graph(data):
    """
    Tái tạo lại đồ thị Python từ dữ liệu JSON của Frontend.
    """
    is_directed_global = data.get('directed', False)
    graph = GraphModel(is_directed=is_directed_global)
    graph.clear()

    max_id = -1
    # 1. Tái tạo Đỉnh
    for node in data.get('nodes', []):
        v_id = int(node['id'])
        v = graph.add_vertex(node['x'], node['y'])
        v.id = v_id
        v.label = node['label']
        graph.vertices[v_id] = v
        if v_id > max_id: max_id = v_id

    graph.next_id = max_id + 1

    # 2. Tái tạo Cạnh
    for edge in data.get('edges', []):
        u_id = int(edge['source'])
        v_id = int(edge['target'])
        weight = 1
        if edge.get('weight') is not None:
            try:
                weight = int(edge['weight'])
            except:
                weight = 1

        new_edge = graph.add_edge(u_id, v_id, weight)
        if new_edge and 'isDirected' in edge:
            new_edge.is_directed = edge['isDirected']

    return graph

# --- ROUTES & API ---

@app.route('/')
def index():
    return render_template('index.html')

# API: BFS Traversal
@app.route('/api/bfs', methods=['POST'])
def run_bfs():
    data = request.json
    graph = rebuild_graph(data['graph'])
    start_id = int(data.get('startId', 0))
    order, edges = bfs_traversal(graph, start_id)
    edge_result = [{"u": e.start_vertex.id, "v": e.end_vertex.id} for e in edges]
    return jsonify({"status": "success", "path": order, "visited_edges": edge_result})

# API: DFS Traversal
@app.route('/api/dfs', methods=['POST'])
def run_dfs():
    data = request.json
    graph = rebuild_graph(data['graph'])
    start_id = int(data.get('startId', 0))
    order, edges = dfs_traversal(graph, start_id)
    edge_result = [{"u": e.start_vertex.id, "v": e.end_vertex.id} for e in edges]
    return jsonify({"status": "success", "path": order, "visited_edges": edge_result})

# API: Shortest Path (Dijkstra)
@app.route('/api/dijkstra', methods=['POST'])
def run_dijkstra():
    data = request.json
    graph = rebuild_graph(data['graph'])
    start_id = int(data.get('startId', 0))
    end_id = int(data.get('endId', 0))
    distance, path = dijkstra_search(graph, start_id, end_id)
    if distance == float('inf'):
        return jsonify({"status": "error", "message": "No path found between these nodes."})
    return jsonify({"status": "success", "distance": distance, "path": path})

# API: Minimum Spanning Tree (Prim / Kruskal)
@app.route('/api/mst', methods=['POST'])
def run_mst():
    data = request.json
    algo_type = data.get('type')
    graph = rebuild_graph(data['graph'])
    mst_edges = []
    if algo_type == 'prim':
        start_id = int(data.get('startId', list(graph.vertices.keys())[0]))
        mst_edges = prim_algorithm(graph, start_id)
    else:
        mst_edges = kruskal_algorithm(graph)
    result_edges = [{"u": e.start_vertex.id, "v": e.end_vertex.id} for e in mst_edges]
    return jsonify({"status": "success", "mst_edges": result_edges})

# ==========================================================
# [UPDATED] API: Euler Path/Circuit (Logic phân loại)
# ==========================================================
@app.route('/api/euler', methods=['POST'])
def run_euler():
    data = request.json
    algo_type = data.get('type')
    graph = rebuild_graph(data['graph'])

    # Lấy đỉnh bắt đầu (quan trọng cho Fleury)
    start_id = int(data.get('startId', list(graph.vertices.keys())[0]))

    success = False
    path = []

    if algo_type == 'fleury':
        success, path = fleury_algorithm(graph, start_id)
    else:
        success, path = hierholzer_algorithm(graph, start_id)

    if not success:
        return jsonify({"status": "error", "message": "Graph does not contain an Euler Path or Circuit."})

    # [LOGIC MỚI] Phân biệt Chu trình (Circuit) hay Đường đi (Path)
    # Nếu đỉnh đầu == đỉnh cuối => Chu trình
    euler_type = "Path"
    if len(path) > 1 and path[0] == path[-1]:
        euler_type = "Circuit"

    return jsonify({
        "status": "success",
        "path": path,
        "euler_type": euler_type # Gửi về Frontend để hiển thị đúng thông báo
    })

# ==========================================================
# [UPDATED] API: Max Flow (Sử dụng NetworkX chuẩn xác)
# ==========================================================
@app.route('/api/max_flow', methods=['POST'])
def run_max_flow():
    try:
        data = request.json
        nodes_data = data['graph']['nodes']
        edges_data = data['graph']['edges']

        if 'sourceId' not in data or 'sinkId' not in data:
            return jsonify({"status": "error", "message": "Please select Source and Sink nodes."})

        source_id = int(data.get('sourceId'))
        sink_id = int(data.get('sinkId'))

        # 1. Tạo đồ thị NetworkX
        G = nx.DiGraph()

        for node in nodes_data:
            G.add_node(int(node['id']))

        for edge in edges_data:
            u = int(edge['source'])
            v = int(edge['target'])
            capacity = int(edge.get('weight', 1))

            # Cộng dồn capacity nếu có nhiều cạnh song song
            if G.has_edge(u, v):
                G[u][v]['capacity'] += capacity
            else:
                G.add_edge(u, v, capacity=capacity)

        # 2. Chạy thuật toán Max Flow
        flow_value, flow_dict = nx.maximum_flow(G, source_id, sink_id)

        # 3. Chuẩn bị dữ liệu chi tiết cho Frontend vẽ màu
        flow_edges_list = []
        for u, v, attrs in G.edges(data=True):
            capacity = attrs['capacity']
            current_flow = flow_dict[u].get(v, 0)

            flow_edges_list.append({
                "u": u,
                "v": v,
                "flow": current_flow,
                "capacity": capacity
            })

        return jsonify({
            "status": "success",
            "max_flow": flow_value,
            "flow_edges": flow_edges_list
        })

    except nx.NetworkXError as e:
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Server Error processing Max Flow"})

# ==========================================================

# API: Check Bipartite
@app.route('/api/bipartite', methods=['POST'])
def run_bipartite():
    data = request.json
    graph = rebuild_graph(data['graph'])
    is_bipartite, color_map = check_bipartite(graph)
    return jsonify({
        "status": "success",
        "is_bipartite": is_bipartite,
        "colors": color_map
    })

# API: Convert Representation
@app.route('/api/convert', methods=['POST'])
def run_convert():
    data = request.json
    mode = data.get('mode')
    graph = rebuild_graph(data['graph'])
    result = ""
    if mode == 'matrix':
        result = get_adjacency_matrix(graph)
    elif mode == 'adj_list':
        result = get_adjacency_list(graph)
    else:
        result = get_edge_list(graph)
    return jsonify({"status": "success", "text": result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
