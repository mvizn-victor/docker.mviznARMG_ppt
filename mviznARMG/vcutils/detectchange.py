from io import StringIO
from PIL import Image
from skimage.metrics import structural_similarity as ssim

def detectchange_ssim(previm, currentim, square_size=50):        
    h, w = previm.shape[:2]
    #square_size = 50
    changes = []

    for y in range(0, h, square_size):
        for x in range(0, w, square_size):
            y_end = min(y + square_size, h)
            x_end = min(x + square_size, w)

            prev_crop = previm[y:y_end, x:x_end]
            curr_crop = currentim[y:y_end, x:x_end]

            if prev_crop.shape != curr_crop.shape:
                continue

            # Convert to grayscale if needed
            if len(prev_crop.shape) == 3:
                prev_crop = cv2.cvtColor(prev_crop, cv2.COLOR_BGR2GRAY)
                curr_crop = cv2.cvtColor(curr_crop, cv2.COLOR_BGR2GRAY)

            ssim_score = ssim(prev_crop, curr_crop)
            score = 1 - ssim_score  # Convert similarity to "change" score

            xc = x + (x_end - x) // 2
            yc = y + (y_end - y) // 2
            changes.append([xc, yc, score])

    return changes

def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)

    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[(i + 1) % n]

        intersect = ((yi > y) != (yj > y)) and \
                    (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi)
        if intersect:
            inside = not inside

    return inside
