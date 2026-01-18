# giúp hard-code màu sắc và kích thước
# file utils/constants.py

# Kích thước
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
CANVAS_BG_COLOR = "#ffffff"
VERTEX_RADIUS = 20

# Màu sắc
VERTEX_COLOR = "#3498db"        # Xanh dương
VERTEX_BORDER_COLOR = "#2980b9"
VERTEX_TEXT_COLOR = "#ffffff"
SELECTED_COLOR = "#e74c3c"      # Đỏ (khi chọn để nối cạnh)
EDGE_COLOR = "#2c3e50"          # Xám đen

# Các chế độ hoạt động (Interaction Modes)
MODE_ADD_VERTEX = "ADD_VERTEX"
MODE_ADD_EDGE = "ADD_EDGE"
MODE_REMOVE = "REMOVE"
MODE_MOVE = "MOVE"
# Màu sắc giao diện
BUTTON_BG_DEFAULT = "#f0f0f0"   # Màu xám mặc định của Windows (hoặc SystemButtonFace)
BUTTON_BG_ACTIVE = "#2ecc71"    # Màu xanh lá (khi được chọn)
BUTTON_TEXT_ACTIVE = "#ffffff"  # Chữ trắng khi nền xanh
BUTTON_TEXT_DEFAULT = "#000000" # Chữ đen mặc định

# Thêm vào cuối file
MODE_ALGO_DIJKSTRA = "mode_algo_dijkstra"
MODE_ALGO_BFS = "mode_algo_bfs"
MODE_ALGO_DFS = "mode_algo_dfs"
MODE_ALGO_BIPARTITE = "mode_algo_bipartite"
MODE_ALGO_PRIM = "mode_algo_prim"
MODE_ALGO_KRUSKAL = "mode_algo_kruskal"
MODE_ALGO_FLEURY = "mode_algo_fleury"
MODE_ALGO_FORD_FULKERSON = "mode_algo_ford_fulkerson"
MODE_ALGO_HIERHOLZER = "mode_algo_hierholzer"
