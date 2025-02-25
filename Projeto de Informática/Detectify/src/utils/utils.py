from PIL import Image
import cv2, fitz, math, numpy as np, os, pandas as pd



class Utils:

    @staticmethod
    def save_image(output_path, image):
        """Save an image to the specified output path."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, image)


    @staticmethod
    def draw_detection(image, class_name, color, x1=None, y1=None, x2=None, y2=None, center_x=None,center_y=None):
        """Draw a detection bounding box and label on an image."""
        if x1 is not None:
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                image,
                f"{class_name}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                thickness=2
            )
        if center_x is not None:
            center = (int(center_x), int(center_y))
            cv2.circle(image, center, 20, color, -1)


    @staticmethod
    def calculate_area(x1, y1, x2, y2):
        """Calculate the area of a bounding box given by (x1, y1) and (x2, y2)."""
        return abs(x2 - x1) * abs(y2 - y1)


    @staticmethod
    def calculate_iou(box1, box2):
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        x1, y1 = max(box1['x1'], box2['x1']), max(box1['y1'], box2['y1'])
        x2, y2 = min(box1['x2'], box2['x2']), min(box1['y2'], box2['y2'])

        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = abs(box1['x2'] - box1['x1']) * abs(box1['y2'] - box1['y1'])
        box2_area = abs(box2['x2'] - box2['x1']) * abs(box2['y2'] - box2['y1'])
        union_area = box1_area + box2_area - inter_area

        return inter_area / union_area if union_area != 0 else 0


    @staticmethod
    def get_center(coords):
        return (coords['x1'] + coords['x2']) // 2, (coords['y1'] + coords['y2']) // 2
    

    @staticmethod
    def get_center_tuple(coords):
        return (coords[0] + coords[2]) // 2, (coords[1] + coords[3]) // 2  


    @staticmethod
    def center_dist(coords1, coords2):

        x1, y1 = coords1[0], coords1[1]
        x2, y2 = coords2[0], coords2[1]

        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


    @staticmethod
    def match_pairs(group1, group2):
        distances = [
            (Utils.center_dist(Utils.get_center(item1), Utils.get_center(item2)), group1_id, group2_id)
            for group1_id, item1 in group1.items()
            for group2_id, item2 in group2.items()
        ]
        
        distances.sort(key=lambda x: x[0])

        matched = set()
        pairs = {}
        for _, group1_id, group2_id in distances:
            if group1_id not in matched and group2_id not in matched:
                pairs[group1_id] = group2_id
                matched.add(group1_id)
                matched.add(group2_id)

        return pairs


    @staticmethod
    def pdf_to_png(pdf_path, output_folder, dpi=210):
        filename_ext = os.path.basename(pdf_path)
        filename_no_ext, _ = os.path.splitext(filename_ext)
        pdf_document = fitz.open(pdf_path)
        pix = pdf_document[0].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
        output_path = os.path.join(output_folder, f'{filename_no_ext}.png')
        pix.save(output_path)
        pdf_document.close()

        return output_path
    

    @staticmethod
    def verify_resolution(path):
        image = Image.open(path)

        if image.size[0] > 8192 or image.size[1] > 8192:
            old_x = image.size[0]
            image.thumbnail((8192, 8192), Image.Resampling.LANCZOS)
            no_ext, ext = os.path.splitext(path)
            new_path = f"{no_ext}_rescale{ext}"
            image.save(new_path)
            
            return new_path, image.size[0] / old_x
        
        return path, 1
    

    @staticmethod
    def pdf_coordinates_to_image(x0, y0, x1, y1, pdf_width, pdf_height, image_width, image_height):
        scale_x = image_width / pdf_width
        scale_y = image_height / pdf_height

        image_x0 = image_width - int(y1 * scale_x)
        image_y0 = int(x0 * scale_y)
        image_x1 = image_width - int(y0 * scale_x)
        image_y1 = int(x1 * scale_y)
    
        return image_x0, image_y0, image_x1, image_y1


    @staticmethod
    def convert_to_serializable(obj):
        if isinstance(obj, np.float32) or isinstance(obj, np.float64):
            return float(obj)

        if isinstance(obj, np.int32) or isinstance(obj, np.int64):
            return int(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        

    @staticmethod
    def process_cables_csv(path):
        df = pd.read_csv(path, dtype={'wire_id': str})
        
        database = {}
        for _, row in df.iterrows():
            custharn = row['custharn']
            triple = (row['wire_id'], row['node1'], row['node2'])
            
            if custharn not in database:
                database[custharn] = []

            database[custharn].append(triple)

        return database


    @staticmethod
    def get_arrow_pointers(image_path, arrow_detections):
        """Extracts the opposite vertex and direction vector for arrow detections."""
        image = cv2.imread(image_path)

        arrow_vectors = {}

        for arrow_id, arrow_coords in arrow_detections.items():
            tile = image[arrow_coords[1]:arrow_coords[3], arrow_coords[0]:arrow_coords[2]]

            gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
            gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, threshold = cv2.threshold(gray_blurred, 50, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                if len(approx) == 3:
                    v1, v2, v3 = approx[0][0], approx[1][0], approx[2][0]

                    d12 = np.linalg.norm(v1 - v2)
                    d13 = np.linalg.norm(v1 - v3)
                    d23 = np.linalg.norm(v2 - v3)

                    if d12 <= d13 and d12 <= d23:
                        opposite_vertex = v3
                        base_vertices = (v1, v2)
                    elif d13 <= d12 and d13 <= d23:
                        opposite_vertex = v2
                        base_vertices = (v1, v3)
                    else:
                        opposite_vertex = v1
                        base_vertices = (v2, v3)

                    midpoint = np.array([(base_vertices[0][0] + base_vertices[1][0]) // 2,
                                         (base_vertices[0][1] + base_vertices[1][1]) // 2])

                    direction_vector = midpoint - opposite_vertex

                    norm = np.linalg.norm(direction_vector)
                    if norm != 0:
                        direction_vector = direction_vector / norm

                    arrow_vectors[arrow_id] = {
                        "opposite_vertex": (
                            int(opposite_vertex[0] + arrow_coords[0]),
                            int(opposite_vertex[1] + arrow_coords[1])
                        ),
                        "direction": direction_vector
                    }
                    break

        return arrow_vectors


    @staticmethod
    def line_intersects_box(start_point, direction, box):
        x0, y0 = start_point
        dx, dy = direction
        x_min, y_min, x_max, y_max = box

        if dx == 0:
            if x_min <= x0 <= x_max:
                t_y1 = (y_min - y0) / dy if dy != 0 else float('inf')
                t_y2 = (y_max - y0) / dy if dy != 0 else float('inf')
                t_y = [min(t_y1, t_y2), max(t_y1, t_y2)]
                return max(t_y[0], 0) <= t_y[1]
            return False
        if dy == 0:
            if y_min <= y0 <= y_max:
                t_x1 = (x_min - x0) / dx if dx != 0 else float('inf')
                t_x2 = (x_max - x0) / dx if dx != 0 else float('inf')
                t_x = [min(t_x1, t_x2), max(t_x1, t_x2)]
                return max(t_x[0], 0) <= t_x[1]
            return False

        t_x1 = (x_min - x0) / dx
        t_x2 = (x_max - x0) / dx
        t_y1 = (y_min - y0) / dy
        t_y2 = (y_max - y0) / dy

        t_x = [min(t_x1, t_x2), max(t_x1, t_x2)]
        t_y = [min(t_y1, t_y2), max(t_y1, t_y2)]

        t_start = max(min(t_x), min(t_y))
        t_end = min(max(t_x), max(t_y))

        return t_start <= t_end and t_end >= 0