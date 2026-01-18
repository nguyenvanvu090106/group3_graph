# file graph/edge.py

class Edge:
    def __init__(self, start_vertex, end_vertex, weight=1, is_directed=False):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.weight = weight
        self.is_directed = is_directed

        # Thuộc tính hỗ trợ highlight đường đi
        self.is_highlighted = False
        # === THÊM DÒNG NÀY ===
        self.color = "black" # Màu mặc định
        self.width = 2       # Độ dày mặc định

    def __repr__(self):
        arrow = "->" if self.is_directed else "--"
        return f"Edge({self.start_vertex.id} {arrow} {self.end_vertex.id})"
