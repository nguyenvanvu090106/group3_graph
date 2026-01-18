# utils/helpers.py
import math

def calculate_distance(x1, y1, x2, y2):
    """Tính khoảng cách giữa 2 điểm."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def is_point_in_circle(x, y, circle_x, circle_y, radius):
    """Kiểm tra xem điểm (x,y) có nằm trong hình tròn không."""
    return calculate_distance(x, y, circle_x, circle_y) <= radius

# === THÊM HÀM NÀY VÀO CUỐI FILE ===
def is_point_near_segment(px, py, x1, y1, x2, y2, threshold=5):
    """
    Kiểm tra điểm (px, py) có nằm gần đoạn thẳng (x1,y1)-(x2,y2) không.
    threshold: Khoảng cách tối đa để tính là 'trúng' (mặc định 5px).
    """
    # 1. Tính độ dài đoạn thẳng bình phương
    line_len_sq = (x1 - x2)**2 + (y1 - y2)**2

    if line_len_sq == 0:
        return is_point_in_circle(px, py, x1, y1, threshold)

    # 2. Tính hình chiếu của điểm lên đường thẳng (tham số t)
    t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len_sq

    # 3. Giới hạn t trong khoảng [0, 1] để đảm bảo điểm nằm TRONG đoạn thẳng
    # (Nếu không có đoạn này, click vào đường kéo dài cũng bị dính)
    t = max(0, min(1, t))

    # 4. Tìm tọa độ điểm hình chiếu gần nhất trên đoạn thẳng
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)

    # 5. Tính khoảng cách từ điểm click đến điểm hình chiếu
    dist_sq = (px - proj_x)**2 + (py - proj_y)**2

    return dist_sq <= threshold**2
