import math, networkx as nx, uuid



class DXF_Graph():
    
    def __init__(self, detections, red_lines, class_configs):
        self.graph = nx.Graph()
        self.positions = {}
        self.edges = {}
        self.detections = detections
        self.possible_nodes = {k: v for k, v in self.detections.items() if class_configs[v['class']]['is_labeled']}
        self.splice_nodes = {k: {'class': 'splice', 'x1': v['arrow_pointer'][0]-10, 'y1': v['arrow_pointer'][1]-10, 'x2': v['arrow_pointer'][0]+10, 'y2': v['arrow_pointer'][1]+10} for k, v in self.detections.items() if v['class'] == 'splice' and 'arrow_pointer' in v}
        self.all_possible_nodes = {**self.possible_nodes, **self.splice_nodes}
        self.red_lines = red_lines
        self.pairs = {}

    
    def update_detections(self, updated_detections):
        self.detections = updated_detections

        for detection_id, detection in self.detections.items():
            if 'label' in detection:
                self.pairs[detection['label']] = detection_id

    
    def line_length(self, start, end):
        """Calculates the length of a line given its start and end coordinates."""
        x1, y1 = start
        x2, y2 = end
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


    def is_within_box(self, coord, box, step=0):
        """Checks if a coordinate is within an expanded bounding box area."""
        x, y = coord
        x1, y1, x2, y2 = box['x1'] - step, box['y1'] - step, box['x2'] + step, box['y2'] + step
        return x1 <= x <= x2 and y1 <= y <= y2
    
    
    def check_is_within_detection_box(self, coord):
        """Checks if a coordinate is within a detection box, including splice nodes."""

        for detection_id, detection in self.all_possible_nodes.items():
            step = -30 if detection['class'] == 'fork' else 20 if detection['class'] == 'olhal' else 0
            if self.is_within_box(coord, detection, step):
                return detection_id
        
        return coord
    

    def get_leaf_nodes(self):
        """Find and return all leaf nodes in the graph."""
        return [node for node in self.graph.nodes if self.graph.degree(node) == 1 and node in self.detections]
    

    def remove_edge(self, edge_id):
        """Remove an edge from the graph."""
        removed_node = self.edges.pop(edge_id)
        self.graph.remove_edge(removed_node['node1'], removed_node['node2'])


    def add_edge(self, node1, node2):
        """Add an edge to the graph between node1 and node2."""
        if self.graph.has_edge(node1, node2):
            return None

        edge_id = str(uuid.uuid4())
        self.graph.add_edge(node1, node2)
        self.edges[edge_id] = {'node1': node1, 'node2': node2}
        return edge_id


    def get_edge(self, node1, node2):
        """Retrieve the edge ID connecting node1 and node2, if it exists."""
        return next(
            (edge_id for edge_id, nodes in self.edges.items() if {node1, node2} == {nodes['node1'], nodes['node2']}),
            None
        )


    def get_shortest_path(self, start_node, end_node):
        """Returns the shortest path between start_node and end_node in the graph."""

        def get_node_variations(node):
            """Generate variations of the node name and return the first valid match, given Database inaccuracies."""
            variations = [
                node,
                node.replace('_', '-'),
                node.replace('-', '_'),
                node.split('_')[0]
            ]
            return next((variant for variant in variations if self.pairs.get(variant)), None)

        
        start_node = get_node_variations(start_node)
        end_node = get_node_variations(end_node)

        if not start_node or not end_node:
            return None

        try:

            path = nx.shortest_path(self.graph, source=self.pairs[start_node], target=self.pairs[end_node])

            return [
                self.get_edge(path[i], path[i + 1]) 
                for i in range(len(path) - 1)
            ]

        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return None
    

    def build_graph(self, min_length=20):
        """Adds nodes to the graph at the endpoints of each segment in polylines."""
        
        for polyline in self.red_lines:
            
            for i in range(len(polyline) - 1):
                start, end = polyline[i], polyline[i + 1]
                length = self.line_length(start, end)

                if length >= min_length:

                    node1 = self.check_is_within_detection_box(start)
                    node2 = self.check_is_within_detection_box(end)

                    if node1 == node2:
                        continue

                    self.graph.add_node(node1)
                    self.graph.add_node(node2)

                    self.positions[node1] = start
                    self.positions[node2] = end
                    
                    if not self.graph.has_edge(node1, node2):
                        self.graph.add_edge(node1, node2, length=length)
                        self.edges[str(uuid.uuid4())] = {'node1': node1, 'node2': node2, 'length': length}