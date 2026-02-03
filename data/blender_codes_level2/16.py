import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
mast_height = 8.0
triangle_side = 1.2
layer_count = 8
layer_height = 1.0
vert_dim = (0.2, 0.2, 1.0)
horiz_dim = (0.2, 0.2, 0.2)
diag_dim = (0.2, 0.2, 1.0)
load_dim = (0.5, 0.5, 0.5)
load_mass = 150.0
base_z = 0.0
top_load_z = 8.25

# Triangle geometry
circumradius = triangle_side / math.sqrt(3)
vertices = [
    Vector((0.0, circumradius, 0.0)),
    Vector((-triangle_side/2, -circumradius/2, 0.0)),
    Vector((triangle_side/2, -circumradius/2, 0.0))
]

# Store all created objects for constraint creation
members = []

def create_member(name, location, scale, rotation=None):
    """Create a cube member with rigid body physics"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if rotation:
        obj.rotation_euler = rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    return obj

# Create vertical members (8 layers × 3 vertices = 24 members)
vertical_objs = []
for layer in range(layer_count):
    z_base = base_z + layer * layer_height
    for v_idx, base_vert in enumerate(vertices):
        loc = Vector((base_vert.x, base_vert.y, z_base + layer_height/2))
        obj = create_member(
            f"Vert_{layer}_{v_idx}",
            loc,
            (vert_dim[0], vert_dim[1], vert_dim[2])
        )
        # Base layer is passive, others active
        if layer == 0:
            obj.rigid_body.type = 'PASSIVE'
        vertical_objs.append(obj)
        members.append(obj)

# Create horizontal bracing at each Z level (9 levels × 3 edges = 27 members)
for level in range(layer_count + 1):
    z_level = base_z + level * layer_height
    for i in range(3):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % 3]
        
        # Edge center
        center = Vector((
            (v1.x + v2.x) / 2,
            (v1.y + v2.y) / 2,
            z_level
        ))
        
        # Edge direction vector
        edge_vec = Vector((v2.x - v1.x, v2.y - v1.y, 0))
        length = edge_vec.length
        
        # Scale cube to span edge length
        scale = (length, horiz_dim[1], horiz_dim[2])
        
        # Rotation to align with edge
        rot = Vector((1, 0, 0)).rotation_difference(edge_vec.normalized()).to_euler()
        
        obj = create_member(
            f"Horiz_{level}_{i}",
            center,
            scale,
            rot
        )
        obj.rigid_body.type = 'ACTIVE'
        members.append(obj)

# Create diagonal members (7 layers × 3 faces × 2 directions = 42 members)
for layer in range(layer_count - 1):
    z_bottom = base_z + layer * layer_height
    z_top = z_bottom + layer_height
    
    for i in range(3):
        v_bottom = vertices[i]
        v_top = vertices[(i + 1) % 3]
        
        # Bottom to top diagonal
        start = Vector((v_bottom.x, v_bottom.y, z_bottom))
        end = Vector((v_top.x, v_top.y, z_top))
        vec = end - start
        length = vec.length
        
        # Scale and rotate
        scale = (diag_dim[0], diag_dim[1], length)
        center = (start + end) / 2
        
        # Rotation: align Z axis with diagonal
        rot = Vector((0, 0, 1)).rotation_difference(vec.normalized()).to_euler()
        
        obj = create_member(
            f"Diag1_{layer}_{i}",
            center,
            scale,
            rot
        )
        obj.rigid_body.type = 'ACTIVE'
        members.append(obj)
        
        # Opposite diagonal (top to bottom)
        start2 = Vector((v_top.x, v_top.y, z_bottom))
        end2 = Vector((v_bottom.x, v_bottom.y, z_top))
        vec2 = end2 - start2
        
        scale2 = (diag_dim[0], diag_dim[1], vec2.length)
        center2 = (start2 + end2) / 2
        
        rot2 = Vector((0, 0, 1)).rotation_difference(vec2.normalized()).to_euler()
        
        obj2 = create_member(
            f"Diag2_{layer}_{i}",
            center2,
            scale2,
            rot2
        )
        obj2.rigid_body.type = 'ACTIVE'
        members.append(obj2)

# Create top load cube
load_cube = create_member(
    "TopLoad",
    Vector((0.0, 0.0, top_load_z)),
    load_dim
)
load_cube.rigid_body.mass = load_mass
members.append(load_cube)

# Create FIXED constraints between all adjacent members
# For simplicity, we'll connect all members that are within threshold distance
constraint_threshold = 0.25  # Max distance for connection

for i, obj1 in enumerate(members):
    for j, obj2 in enumerate(members[i+1:], i+1):
        dist = (obj1.location - obj2.location).length
        
        if dist < constraint_threshold:
            bpy.ops.rigidbody.constraint_add()
            constraint = bpy.context.active_object
            constraint.rigid_body_constraint.type = 'FIXED'
            constraint.rigid_body_constraint.object1 = obj1
            constraint.rigid_body_constraint.object2 = obj2
            
            # Set pivot at midpoint
            midpoint = (obj1.location + obj2.location) / 2
            constraint.location = midpoint

# Verify structure height
top_verts = [obj for obj in vertical_objs if abs(obj.location.z - 8.5) < 0.1]
print(f"Created {len(members)} members with {len(bpy.data.objects)} total objects")
print(f"Top vertices at Z={[v.location.z for v in top_verts]}")