from utils.dxf_reader import DXF_Reader
from utils.utils import Utils
import cv2, json, math, re, uuid



class DXF_Interpreter():

    def __init__(self, dxf_filepath, dxf_v1_filepath, image_path, configs_filepath):
        self.dxf_data = DXF_Reader.read_dxf(dxf_filepath)
        self.v1_data = DXF_Reader.read_dxf(dxf_v1_filepath)
        self.class_configs = configs_filepath
        self.cad_height, self.cad_width = self.get_board_dimensions()

        image = cv2.imread(image_path)
        self.image_height, self.image_width, _ = image.shape

        self.detections = {}
        self.all_text = self.get_text()

    
    def get_red_lines(self):
        """Extracts and maps red polyline geometries from the DXF data."""
        return [
            [self.map_coordinates(point[0], point[1]) for point in entity["geometry"]]
            for entity in self.v1_data.get("*Model_Space", [])
            if entity.get("type") == "POLYLINE" and entity.get("attributes", {}).get("color") == 1
        ]
        

    def map_coordinates(self, x, y):
        """Map CAD coordinates to image coordinates."""
        return (x / self.cad_width) * self.image_width, self.image_height - (y / self.cad_height) * self.image_height

    
    def get_text(self):
        """Get all textual elements from Model Space."""
        return [
            {
                'text': entity['attributes']['text'],
                'layer': entity['attributes']['layer'],
                'coords': self.map_coordinates(*entity['attributes']['insert'][:2])
            }
            for entity in self.dxf_data.get("*Model_Space", [])
            if entity['type'] == 'TEXT'
        ]


    def map_radius(self, radius):
        """Map CAD radius to image radius."""
        x_scale = self.image_width / self.cad_width
        y_scale = self.image_height / self.cad_height
        return radius * (x_scale + y_scale) / 2


    def rotate_point(self, x, y, cx, cy, angle):
        """Rotates a point (x, y) around a center (cx, cy) by a given angle in degrees."""
        radians = math.radians(-angle)
        dx, dy = x - cx, y - cy
        new_x = cx + (dx * math.cos(radians) - dy * math.sin(radians))
        new_y = cy + (dx * math.sin(radians) + dy * math.cos(radians))
        return new_x, new_y
    

    def update_bounds(self, x, y, bounds):
        """Update the bounding box limits."""
        min_x, min_y, max_x, max_y = bounds
        return (
            min(min_x, x), min(min_y, y),
            max(max_x, x), max(max_y, y)
        )


    def calculate_limits(self, items, padding=5):
        """Calculate the bounding box limits for a set of items in CAD space, mapped to image coordinates."""
        bounds = float("inf"), float("inf"), float("-inf"), float("-inf")
        
        for item in items:
            if item["type"] == "POLYLINE":
                for x, y in map(lambda p: self.map_coordinates(p[0], p[1]), item["geometry"]):
                    bounds = self.update_bounds(x, y, bounds)

            elif item["type"] == "CIRCLE":
                radius = self.map_radius(item["attributes"]["radius"])
                center = item['attributes']['center']
                cx, cy = self.map_coordinates(center[0], center[1])
                circle_points = [
                    (cx - radius, cy - radius),
                    (cx + radius, cy + radius)
                ]

                for x, y in circle_points:
                    bounds = self.update_bounds(x, y, bounds)

            elif item["type"] == "SOLID":
                vertices = [
                    item["attributes"].get(f"vtx{i}") for i in range(4)
                ]

                for vertex in filter(None, vertices):
                    x, y = self.map_coordinates(vertex[0], vertex[1])
                    bounds = self.update_bounds(x, y, bounds)

        min_x, min_y, max_x, max_y = bounds
        return (min_x - padding, min_y - padding), (max_x + padding, max_y + padding)


    def get_board_dimensions(self):
        """Extract the board dimensions (width, height)."""
        for key in list(self.dxf_data):
            if key.startswith("B_"):
                match = re.search(r"B_(\d+)_X_(\d+)", key)

                if match:
                    del self.dxf_data[key]
                    return int(match.group(1)), int(match.group(2))
                

    def line_intersection(self, line1, line2):
        """If any, calculates the point of intersection between two line segments."""
        x1, y1, x2, y2 = *line1[0], *line1[1]
        x3, y3, x4, y4 = *line2[0], *line2[1]

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None

        t1 = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        t2 = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom

        if 0 <= t1 <= 1 and 0 <= t2 <= 1:
            px = x1 + t1 * (x2 - x1)
            py = y1 + t1 * (y2 - y1)
            return px, py

        return None


    def find_limits(self, limits, insert_coords, radius, drilling_points=None):
        "Calculates the adjusted and rotated component limits, together with drilling points, if supplied."
        center_x = (limits[0][0] + limits[1][0]) / 2
        center_y = (limits[0][1] + limits[1][1]) / 2

        adjusted_corners = [
            (corner[0] - center_x + insert_coords[0], corner[1] - center_y + insert_coords[1])
            for corner in [
                limits[0], (limits[1][0], limits[0][1]),
                limits[1], (limits[0][0], limits[1][1]),
            ]
        ]

        rotated_corners = [
                self.rotate_point(x, y, insert_coords[0], insert_coords[1], radius)
                for x, y in adjusted_corners
            ]

        rotated_drilling_points = [
            self.rotate_point(
                point[0] - center_x + insert_coords[0],
                point[1] - center_y + insert_coords[1],
                insert_coords[0],
                insert_coords[1],
                radius
            )
            for point in drilling_points
        ] if drilling_points else None


        x_values, y_values = zip(*rotated_corners)
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)

        return (min_x, min_y, max_x, max_y), rotated_drilling_points
    

    def add_detection(self, class_name, component_limits, insert_coords=None, drilling_points=None, text=None, arrow_pointer=None, label=None):
        detection_id = str(uuid.uuid4())

        if any(map(lambda x: x is None or x != x, component_limits)):
            return None

        self.detections[detection_id] = {
            'class': class_name,
            'x1': int(component_limits[0]),
            'y1': int(component_limits[1]),
            'x2': int(component_limits[2]),
            'y2': int(component_limits[3]),
            **({'text': text} if text else {}),
            **({'label': label} if label else {}),
            **({'insert_coords': insert_coords} if insert_coords else {}),
            **({'arrow_pointer': arrow_pointer} if arrow_pointer else {}),
            **({'drilling_points': drilling_points} if drilling_points else {})
        }

        if class_name in ['fork', 'assembly_guide']:
            self.detections[detection_id]['drilling_points'] = [insert_coords]

    
    def get_limits_by_prefix(self, prefix):
        """Retrieves and calculates limits for entities in the DXF data whose keys start with the given prefix."""
        items = {k: v for k, v in self.dxf_data.items() if k.startswith(prefix) and 'MOD' not in k}

        return {
            item: self.calculate_limits(entities) for item, entities in items.items()
        }


    def process_entities_by_prefix(self, prefix, class_name):
        """Processes entities in the DXF data based on a given prefix and class name, calculating limits."""
        limits = self.get_limits_by_prefix(prefix)

        for entity in self.dxf_data.get("*Model_Space", []):
            attributes = entity.get("attributes", {})

            if entity["type"] == "INSERT" and (name := attributes.get("name")) in limits:

                insert_coords = self.map_coordinates(*attributes["insert"][:2])
                rotation = attributes.get("rotation", 0)

                component_limits, drilling_points = self.find_limits(limits[name], insert_coords, rotation)
                self.add_detection(class_name, component_limits, text=name, insert_coords=insert_coords, drilling_points=drilling_points)


    def get_node_lines(self):
        """Retrieves vertical lines from POLYLINE entities in the DXF data, filtering by layer and red color."""
        return [
            (geometry[0][0], abs(geometry[0][1] + geometry[1][1]) / 2)
            for entity in self.dxf_data.get("*Model_Space", [])
            if (
                entity["type"] == "POLYLINE"
                and entity.get("attributes", {}).get("layer") == "SELECTION"
                and entity["attributes"].get("color") == 1
                and len(entity["geometry"]) == 2
                and (geometry := [self.map_coordinates(point[0], point[1]) for point in entity["geometry"]])[0][0] == geometry[1][0]
            )
        ]
    

    def get_nodes(self):
        """Processes text entities and associates them with the nearest node line to create node detections."""
        node_lines = self.get_node_lines()

        nodes = [
            {'text': text['text'], 'center': text['coords']}
            for text in self.all_text if text['layer'] == 'NODES'
        ]

        for item in nodes:
            center, text = item['center'], item['text']

            _, best_endpoint = min(
                ((Utils.center_dist(center, node_point), node_point) for node_point in node_lines),
                key=lambda x: x[0]
            )

            self.detections[str(uuid.uuid4())] = {
                'class': 'node',
                'value': text,
                'center': best_endpoint
            }


    def get_straight_lines(self):
        """Retrieves straight lines from the DXF data, excluding those on the 'COVERINGS' layer or with color 1."""
        return [
            (geometry[0], geometry[1])
            for entity in self.dxf_data.get("*Model_Space", [])
            if (
                entity['type'] == 'POLYLINE'
                and entity.get('attributes', {}).get('layer') != 'COVERINGS'
                and entity['attributes'].get('color') != 1
                and len((geometry := [self.map_coordinates(point[0], point[1]) for point in entity["geometry"]])) == 2
            )
        ]
    

    def get_mm(self):
        """Extracts 'mm' measurements from text entities, associates them with the measurement point on the cable course."""
        lines = self.get_straight_lines()

        mm = [
            {'value': int(match.group(1)), 'center': text['coords']}
            for text in self.all_text if (match := re.match(r'(\d+)mm', text['text']))
        ]

        for item in mm:
            center, value = item['center'], item['value']

            _, best_endpoint = min(
                ((Utils.center_dist(center, start_point), end_point) for start_point, end_point in lines),
                key=lambda x: x[0]
            )

            self.detections[str(uuid.uuid4())] = {
                'class': 'mm',
                'value': value,
                'center': best_endpoint
            }

    
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculates the perpendicular distance from a point to a line segment."""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end

        if x1 == x2 and y1 == y2:
            return float('inf')

        num = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        den = ((y2 - y1)**2 + (x2 - x1)**2)**0.5
        return num / den
    


    def find_pointer_vertex(self, polygon):
        """Identifies the vertex in a triangular polygon that forms the "pointer" (the vertex furthest from the opposite side)."""
        if len(polygon) != 3:
            return None

        p1, p2, p3 = polygon

        dist1 = self.point_to_line_distance(p3, p1, p2)
        dist2 = self.point_to_line_distance(p1, p2, p3)
        dist3 = self.point_to_line_distance(p2, p1, p3)

        distances = [(dist1, p3), (dist2, p1), (dist3, p2)]
        pointer_vertex = max(distances, key=lambda x: x[0])[1]

        return pointer_vertex



    def get_tube_pointers(self):
        """Extracts pointer coordinates from 'SOLID' entities in the 'TEXT' layer."""
        tube_pointers = []

        for entity in self.dxf_data.get("*Model_Space", []):
            attributes = entity.get("attributes", {})

            if entity['type'] == 'SOLID' and attributes['layer'] == 'TEXT':
                vertices = [
                    attributes.get(f"vtx{i}", [])
                    for i in range(4)
                ]
                polygon = [
                    self.map_coordinates(v[0], v[1])
                    for v in vertices if v
                ]

                polygon = polygon[:-1]
                if len(polygon) == 3:
                    tube_pointers.append(self.find_pointer_vertex(polygon))

        return tube_pointers


    def get_tubes(self):
        """Processes tubes by matching text labels starting with 'TUBO' to arrow pointers."""
        tube_pointers = self.get_tube_pointers()

        tubes = [
            {'text': text['text'], 'center': text['coords']}
            for text in self.all_text if text['text'].startswith('TUBO')
        ]

        distances = sorted(
            (
                (Utils.center_dist(tube['center'], tube_pointer), tube_pointer, tube['text'], tube['center'])
                for tube_pointer in tube_pointers
                for tube in tubes
            ),
            key=lambda x: x[0]
        )

        matched = set()
        for _, tube_pointer, tube_text, tube_center in distances:
            if tube_center not in matched:
                x, y = tuple(map(int, tube_center))
                
                self.add_detection(
                    class_name='tubo', 
                    component_limits=(x - 10, y - 50, x + 210, y + 10), 
                    text=tube_text, 
                    arrow_pointer=tuple(map(int, tube_pointer))
                )

                matched.add(tube_center)


    def is_inside(self, inner, outer):
        """Checks if one rectangular region (inner) is completely contained within another (outer)."""
        return (
            inner["x1"] >= outer["x1"]
            and inner["y1"] >= outer["y1"]
            and inner["x2"] <= outer["x2"]
            and inner["y2"] <= outer["y2"]
        )


    def get_splice_boxes(self):
        """Extracts and groups polyline-based boxes from DXF entities in the 'SYMBOLS' layer."""
        boxes = [
            {
                "x1": min(x_coords := [point[0] for point in geometry]),
                "y1": min(y_coords := [point[1] for point in geometry]),
                "x2": max(x_coords),
                "y2": max(y_coords)
            }
            for entity in self.dxf_data.get("*Model_Space", [])
            if entity['type'] == 'POLYLINE'
            and entity.get('attributes', {}).get('layer') == 'SYMBOLS'
            if len((geometry := [self.map_coordinates(point[0], point[1]) for point in entity["geometry"]])) > 3
        ]

        
        groups = {}
        visited = set()

        for i, box in enumerate(boxes):
            if i not in visited:
                
                nested_boxes = [
                    other_box
                    for j, other_box in enumerate(boxes)
                    if i != j and self.is_inside(other_box, box) and j not in visited
                ]

                if nested_boxes:
                    groups[f'{box["x1"]}_{box["y1"]}_{box["x2"]}_{box["y2"]}'] = nested_boxes
                    visited.update([i] + [j for j in range(len(boxes)) if self.is_inside(boxes[j], box)])

        return groups
    

    def get_splice_lines(self):
        """Extracts straight lines (POLYLINE with two points) from DXF entities in the 'SYMBOLS' layer."""
        return [
            [self.map_coordinates(point[0], point[1]) for point in entity["geometry"]]
            for entity in self.dxf_data.get("*Model_Space", [])
            if entity['type'] == 'POLYLINE' and entity.get('attributes', {}).get('layer') == 'SYMBOLS'
            if len(entity["geometry"]) == 2
        ]
    

    def map_splice_wires(self):
        """Associates wires (text entities) with the corresponding splice detection based on coordinates."""
        splices = {k: v for k, v in self.detections.items() if v['class'] == 'splice'}

        for text in self.all_text:
            if text['layer'] == 'SYMBOLS' and text['text'].isnumeric():

                coords_x, coords_y = text['coords']

                found_text = next((
                    splice_id for splice_id, splice in splices.items()
                    if splice['x1'] <= coords_x <= splice['x2'] and splice['y1'] <= coords_y <= splice['y2']
                ), None)

                if found_text:
                    self.detections[found_text].setdefault('wires', []).append(text['text'])

    
    def get_splices(self):
        splice_boxes = self.get_splice_boxes()
        splice_lines = self.get_splice_lines()

        nodes = {k: v for k, v in self.detections.items() if v['class'] == 'node'}
        splices = [
            {'text': text['text'], 'center': text['coords']}
            for text in self.all_text if text['text'].startswith('S') and ',,,' in text['text']
        ]

 
        for item in splices:
            center = item['center']
            text = item['text']

            best_box = min(
                splice_boxes.items(),
                key=lambda item: Utils.center_dist(center, Utils.get_center_tuple(tuple(map(int, list(map(float, item[0].split('_')))))))
            )[0]

            best_box = tuple(map(int, list(map(float, best_box.split('_')))))

            for pt1, pt2 in splice_lines:
                if (abs(pt2[0] - best_box[0]) < 10 and best_box[1] <= pt2[1] <= best_box[3]) or \
                    (abs(pt2[1] - best_box[1]) < 10 and best_box[0] <= pt2[0] <= best_box[2]) or \
                    (abs(pt2[0] - best_box[2]) < 10 and best_box[1] <= pt2[1] <= best_box[3]) or \
                    (abs(pt2[1] - best_box[3]) < 10 and best_box[0] <= pt2[0] <= best_box[2]):

                    pt1 = tuple(map(int, pt1))

                    best_node = min(
                        nodes.items(),
                        key=lambda item: Utils.center_dist(tuple(map(int, item[1]['center'])), pt1)
                    )[0]

                    splice_id = str(uuid.uuid4())

                    self.detections[best_node]['splice'] = splice_id

                    box = tuple(map(int, best_box))
                    self.detections[splice_id] = {
                        'class': 'splice',
                        'x1': box[0],
                        'y1': box[1],
                        'x2': box[2],
                        'y2': box[3],
                        'arrow_pointer': tuple(map(int, self.detections[best_node]['center'])),
                        'label': text.split(',')[0]
                    }

                    break
        
        self.map_splice_wires()


    def get_wire_boxes_limits(self):
        "Calculates the possible wire_box limits, based on exclusivity rules on Model Space blocks."
        possible_wire_boxes = {}
        for key, v in self.dxf_data.items():
            if not key.startswith("B_") and not key.startswith("2P") and not key.startswith("1P") and not key.startswith("1E") and not key.startswith("P0") \
                and 'MODBI' not in key and 'LISTA' not in key and 'BOARD' not in key and 'INFO' not in key \
                and key not in ['*Model_Space', '*Paper_Space', '$HANDTAPE$', '$SPIRALTAPE$', '$SPACETAPE$', 'PROAGCO']:
                
                possible_wire_boxes[key] = v

        
        return {
            component_id: self.calculate_limits(entities) for component_id, entities in possible_wire_boxes.items()
        }
    

    def get_wire_box_lines(self):
        """Retrive wire_box related pointing lines."""
        return [
            [self.map_coordinates(point[0], point[1]) for point in entity["geometry"]]
            for entity in self.dxf_data.get("*Model_Space", [])
            if entity['type'] == 'POLYLINE' and entity.get("attributes", {}).get('layer') == 'SYMBOLS'
            and len(entity["geometry"]) == 2
        ]


    def get_wire_boxes(self):
        wire_boxe_limits = self.get_wire_boxes_limits()

        for entity in self.dxf_data.get("*Model_Space", []):
            attributes = entity.get("attributes", {})

            if entity["type"] == "INSERT" and (name := attributes.get("name")) in wire_boxe_limits:
                
                insert_coords = self.map_coordinates(*attributes["insert"][:2])
                rotation = attributes.get("rotation", 0)

                component_limits, _ = self.find_limits(wire_boxe_limits[name], insert_coords, rotation)
                self.add_detection('wire_box', component_limits, insert_coords=insert_coords)


    def map_wire_boxes_w_arrow_to_nodes(self, leaf_nodes):
        nodes = { node: self.detections[node] for node in leaf_nodes }
        wire_boxes_w_arrow = {k: v for k, v in self.detections.items() if v['class'] == 'wire_box' and 'arrow_pointer' in v}

        def calculate_distances(wire_boxes, distance_key):
            return [
                (Utils.center_dist(node['insert_coords'], Utils.get_center(wire_box) if distance_key == 'center' else wire_box['arrow_pointer']),
                node_id, wire_box_id)
                for node_id, node in nodes.items()
                for wire_box_id, wire_box in wire_boxes.items()
            ]

        distances_w_arrow = calculate_distances(wire_boxes_w_arrow, 'arrow_pointer')
        distances_w_arrow.sort(key=lambda x: x[0])

        matched = set()

        def assign_nodes(distances):
            for _, node_id, wire_box_id in distances:
                if wire_box_id not in matched and node_id not in matched:
                    self.detections[wire_box_id]['object'] = node_id
                    matched.add(wire_box_id)
                    matched.add(node_id)

                    if 'arrow_pointer' in self.detections[wire_box_id]:
                        del self.detections[wire_box_id]['arrow_pointer']

        assign_nodes(distances_w_arrow)



    def map_wire_boxes(self):
        self.get_wire_boxes()
        
        possible_wire_boxes = {k: v for k, v in self.detections.items() if v['class'] == 'wire_box'}
        possible_wire_boxe_lines = self.get_wire_box_lines()

        for text in self.all_text:
            if text['layer'] == 'SYMBOLS' and text['text'].isnumeric():
                coords_x, coords_y = text['coords']

                found_text = next((
                        node_id
                        for node_id, node in possible_wire_boxes.items()
                        if node['x1'] <=  coords_x <= node['x2'] and node['y1'] <= coords_y <= node['y2'])
                    , None)

                if found_text:
                    self.detections[found_text].setdefault('wires', []).append(text['text'])
                    wire_box = self.detections[found_text]
                    wire_box = wire_box['x1'], wire_box['y1'], wire_box['x2'], wire_box['y2']

                    for pt1, pt2 in possible_wire_boxe_lines:
                        if (abs(pt2[0] - wire_box[0]) < 10 and wire_box[1] <= pt2[1] <= wire_box[3]) or \
                            (abs(pt2[1] - wire_box[1]) < 10 and wire_box[0] <= pt2[0] <= wire_box[2]) or \
                            (abs(pt2[0] - wire_box[2]) < 10 and wire_box[1] <= pt2[1] <= wire_box[3]) or \
                            (abs(pt2[1] - wire_box[3]) < 10 and wire_box[0] <= pt2[0] <= wire_box[2]) or \
                                wire_box[0] <= pt2[0] <= wire_box[2] and wire_box[1] <= pt2[1] <= wire_box[3]:

                            self.detections[found_text]['arrow_pointer'] = tuple(map(int, pt1))

        for detection_id in possible_wire_boxes:
            if 'wires' not in self.detections[detection_id]:
                del self.detections[detection_id]



    def get_MOD_BI_nuclear_points(self, entities):
        lines = []
        drilling_points = []
        for item in entities:
            if item["type"] == "POLYLINE" and item['attributes']['color'] == 1:
                geometry = [self.map_coordinates(point[0], point[1]) for point in item["geometry"]] 

                if len(geometry) == 2:
                    (x1, y1), (x2, y2) = geometry

                    if abs(y2 - y1) == 0 or abs(x2 - x1) == 0:
                        lines.append(geometry)


            elif item["type"] == "CIRCLE" and (item['attributes']['radius'] == 2.9997 or item['attributes']['radius'] == 2.9992):
                center = item['attributes']['center']
                center = self.map_coordinates(center[0], center[1])

                drilling_points.append(center)
                
        
        min_intersection = float("inf"), float("inf")

        if len(lines) == 2:
            min_intersection = self.line_intersection(lines[0], lines[1])
        
        else:

            for i, line1 in enumerate(lines):
                for j, line2 in enumerate(lines):
                    if i >= j: 
                        continue
                    intersection = self.line_intersection(line1, line2)
                    if intersection and intersection[1] < min_intersection[1]:
                        min_intersection = intersection

        return min_intersection, drilling_points
        

    def get_MOD_BI_limits(self, pattern):
        modbis = {k: v for k, v in self.dxf_data.items() if pattern in k}
        
        res = {}
        for modbi, entities in modbis.items():
            module_insert_point, drilling_points = self.get_MOD_BI_nuclear_points(entities)

            (x1, y1), (x2, y2) = self.calculate_limits(entities)
            center = Utils.get_center_tuple((x1, y1, x2, y2))

            translation = (center[0] - module_insert_point[0], center[1] - module_insert_point[1])

            res[modbi] = { "limits": ((x1, y1), (x2, y2)), "drilling_points": drilling_points, "translation": translation} 
        
        return res
        

    def get_MOD_BI(self, pattern):
        modbi_limits = self.get_MOD_BI_limits(pattern)

        for entity in self.dxf_data.get("*Model_Space", []):
            attributes = entity.get("attributes", {})

            if entity["type"] == "INSERT" and (name := attributes.get("name")) in modbi_limits:
                
                insert_coords = self.map_coordinates(*attributes["insert"][:2])
                rotation = attributes.get("rotation", 0)
            
                limits = modbi_limits[name]

                translation = limits["translation"]
                updated_coords = (
                    insert_coords[0] + translation[0],
                    insert_coords[1] + translation[1]
                )

                updated_coords = (
                    self.rotate_point(updated_coords[0], updated_coords[1], insert_coords[0], insert_coords[1], rotation)
                )

                component_limits, drilling_points = self.find_limits(limits['limits'], updated_coords, rotation, limits['drilling_points'])
                self.add_detection("big_node", component_limits, insert_coords=updated_coords, drilling_points=drilling_points)
    

    def get_label_variation(self, node, labels):
        variations = [
            node,
            node.replace('_', '-'),
            node.replace('-', '_'),
            node.split('_')[0]
        ]
        return next((variant for variant in variations if variant in labels), None)
            


    def label_components(self, leaf_nodes):
        labels = {}
        wire_boxes = { k: v for k, v in self.detections.items() if v['class'] == 'wire_box' }

        old_labels = [
            {'text': text['text'].split(',')[0], 'center': text['coords']}
            for text in self.all_text if not text['text'].startswith('S') and ',,,' in text['text']
        ]

        for entity in self.dxf_data.get("*Model_Space", []):
            attributes = entity.get("attributes", {})

            if entity["type"] == "SOLID" and attributes.get("color", 0) == 11:

                bounds = float("inf"), float("inf"), float("-inf"), float("-inf")

                vertices = [
                    entity["attributes"].get(f"vtx{i}") for i in range(4)
                ]

                for vertex in filter(None, vertices):
                    x, y = self.map_coordinates(vertex[0], vertex[1])
                    bounds = self.update_bounds(x, y, bounds)

                min_x, min_y, max_x, max_y = bounds

                found_text = next((
                        item['text']
                        for item in self.all_text
                        if min_x <= item['coords'][0] <= max_x and min_y <= item['coords'][1] <= max_y and item['text'] not in self.dxf_data.keys()
                    ), None)

                labels[str(uuid.uuid4())] = {
                    'x1': int(min_x),
                    'y1': int(min_y),
                    'x2': int(max_x),
                    'y2': int(max_y),
                    'text': found_text
                }

        text_labels = [ label['text'] for _, label in labels.items() ]

        for old_label in old_labels:
            existing_label = self.get_label_variation(old_label['text'], text_labels)
            
            if not existing_label:
                labels[str(uuid.uuid4())] = {
                    'x1': int(old_label['center'][0]-5),
                    'y1': int(old_label['center'][1]-5),
                    'x2': int(old_label['center'][0]+5),
                    'y2': int(old_label['center'][1]+5),
                    'text': old_label['text']
                }

        pairs = Utils.match_pairs(labels, wire_boxes)
        matched = set()

        for label_id, wire_box_id in pairs.items():
            if label_id not in matched and wire_box_id not in matched:
                wire_box = self.detections[wire_box_id]
                if 'object' in wire_box:
                    self.detections[wire_box['object']]['label'] = labels[label_id]["text"]
                else:
                    self.detections[wire_box_id]['label'] = labels[label_id]["text"]
                matched.add(label_id)
                matched.add(wire_box_id)

        remaining_wire_boxes = wire_boxes = { k: v for k, v in self.detections.items() if v['class'] == 'wire_box' and 'label' not in v }
        pairs = Utils.match_pairs(labels, remaining_wire_boxes)
        matched = set()

        for label_id, wire_box_id in pairs.items():
            if label_id not in matched and wire_box_id not in matched:
                wire_box = self.detections[wire_box_id]
                if 'object' in wire_box:
                    self.detections[wire_box['object']]['label'] = labels[label_id]["text"]
                else:
                    self.detections[wire_box_id]['label'] = labels[label_id]["text"]
                matched.add(label_id)
                matched.add(wire_box_id)

        
        possible_nodes = { node: self.detections[node] for node in leaf_nodes if 'label' not in self.detections[node] }
        wire_boxes = { k: v for k, v in self.detections.items() if v['class'] == 'wire_box' and 'label' in v }

        matched = set()

        pairs = Utils.match_pairs(possible_nodes, wire_boxes)
        for node_id, wire_box_id in pairs.items():
            if node_id not in matched and wire_box_id not in matched:
                self.detections[wire_box_id]['object'] = node_id
                self.detections[node_id]['label'] = self.detections[wire_box_id]['label']
                del self.detections[wire_box_id]['label']
                matched.add(node_id)
                matched.add(wire_box_id)

        wire_boxes = { k: v for k, v in self.detections.items() if v['class'] == 'wire_box' and 'label' in v }
        for wire_box_id, w in wire_boxes.items():
            del self.detections[wire_box_id]['label']

        
        
        
    def get_clips(self):
        """Identifies and processes 'clip' elements, assigning them to the closest 'component' in the detections."""
        clips = [
            {'text': text['text'], 'center': text['coords']}
            for text in self.all_text if 'clip' in text['text'].lower()
        ]

        components = { k: v for k, v in self.detections.items() if v['class'] == 'component' }

        for clip in clips:

            best_component = min(
                    components.items(),
                    key=lambda item: Utils.center_dist(clip['center'], Utils.get_center(item[1]))
                )[0]
            
            self.detections[best_component]['class'] = 'clip'
            self.detections[best_component]['clip_id'] = clip['text']


    def drilling_points_severance(self):
        for detection_id in list(self.detections):
            if 'drilling_points' in self.detections[detection_id]:
        
                for drilling_point in self.detections[detection_id]['drilling_points']:
                   
                    self.detections[str(uuid.uuid4())] = {
                        'class': 'drilling_point',
                        'center': tuple(map(int, drilling_point))
                    }


    def process_dxf_file(self):
        self.get_nodes()
        self.process_entities_by_prefix("2P6", "fork")
        self.process_entities_by_prefix("2P_", "clamp")
        self.process_entities_by_prefix("1P55_MARCA", "perno_marca")
        self.process_entities_by_prefix("1P65_6L", "pin")
        self.process_entities_by_prefix("1P60_6", "assembly_guide")
        self.process_entities_by_prefix("1E", "olhal")
        self.process_entities_by_prefix('$SPACETAPE$', 'markings_up')
        self.process_entities_by_prefix('$SPIRALTAPE$', 'spiral_up')
        self.process_entities_by_prefix('$HANDTAPE$', 'total_bandage_up')
        self.process_entities_by_prefix('$USPACETAPE$', 'markings_down')
        self.process_entities_by_prefix('P0', 'component')
        self.get_clips()
        self.get_mm()
        self.get_tubes()
        self.get_splices()
        self.get_MOD_BI('MODBI')
        self.get_MOD_BI('MOD')
        self.map_wire_boxes()


    def process_pos_graph(self, leaf_nodes):
        self.map_wire_boxes_w_arrow_to_nodes(leaf_nodes)
        self.label_components(leaf_nodes)


    @staticmethod
    def get_wire_connections(detections):
        wire_nodes = {k: v for k, v in detections.items() if 'wires' in v}
        wire_map = {}

        for _, wire_nodes in wire_nodes.items():
            label = wire_nodes['label'] if wire_nodes['class'] == 'splice' else detections[wire_nodes['object']]['label'] if 'object' in wire_nodes and 'label' in detections[wire_nodes['object']] else None
            if not label:
                continue

            for wire in wire_nodes['wires']:
                wire_map.setdefault(wire, []).append(label)

        connections = {wire: splices for wire, splices in wire_map.items() if len(splices) > 1}

        return [
            (wire, node[0], node[1]) for wire, node in connections.items() if node[0] != node[1]
        ]