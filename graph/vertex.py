# file graph/vertex.py

class Vertex:
    def __init__(self, vertex_id, x, y, label=None):
        self.id = vertex_id
        self.x = x
        self.y = y
        self.label = label if label else str(vertex_id)
# === THÊM DÒNG NÀY ===
        self.color = "#3498db" # Màu mặc định (Xanh dương)
        self.border_color = "black"
    def __repr__(self):
        return f"Vertex({self.id}, {self.label})"
