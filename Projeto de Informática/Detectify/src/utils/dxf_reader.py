import ezdxf



class DXF_Reader():

    @staticmethod
    def read_dxf(dxf_filepath):
        doc = ezdxf.readfile(dxf_filepath)
        data = {}

        for block in doc.blocks:
            data[block.name] = []
      
            for entity in block:
                entity_data = {
                    "type": entity.dxftype(),
                    "attributes": {},
                    "geometry": {}
                }


                for key, value in entity.dxfattribs().items():
                    if isinstance(value, ezdxf.math.Vec3):
                        entity_data["attributes"][key] = [value.x, value.y, value.z]
                    else:
                        entity_data["attributes"][key] = value


                if entity.dxftype() == "LINE":
                    entity_data["geometry"] = {
                        "start": [entity.dxf.start.x, entity.dxf.start.y, entity.dxf.start.z],
                        "end": [entity.dxf.end.x, entity.dxf.end.y, entity.dxf.end.z]
                    }
                elif entity.dxftype() == "POLYLINE":
                    entity_data["geometry"] = [
                        [vertex.dxf.location.x, vertex.dxf.location.y, vertex.dxf.location.z]
                        for vertex in entity.vertices
                    ]
                elif entity.dxftype() == "CIRCLE":
                    entity_data["geometry"] = {
                        "center": [entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z],
                        "radius": entity.dxf.radius
                    }
                elif entity.dxftype() == "ARC":
                    entity_data["geometry"] = {
                        "center": [entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z],
                        "radius": entity.dxf.radius,
                        "start_angle": entity.dxf.start_angle,
                        "end_angle": entity.dxf.end_angle
                    }
                elif entity.dxftype() in ["TEXT", "MTEXT"]:
                    entity_data["geometry"] = {
                        "text": entity.dxf.text,
                        "insert_point": [entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z]
                    }
                elif entity.dxftype() == "HATCH":
                    entity_data["geometry"] = {
                        "pattern_name": entity.dxf.pattern_name,
                        "solid_fill": entity.dxf.solid_fill,
                        "edges": [[edge.start_point, edge.end_point] for edge in entity.paths.edges]
                    }
                elif entity.dxftype() == "DIMENSION":
                    entity_data["geometry"] = {
                        "dimension_type": entity.dxf.dimension_type,
                        "measurement": entity.dxf.text,
                        "geometry": str(entity.dimension_block_reference()) if entity.dimension_block_reference() else None
                    }

                data[block.name].append(entity_data)

        return data