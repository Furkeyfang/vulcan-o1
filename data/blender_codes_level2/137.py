import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# ------------------------------------------------------------
# Parameters from summary
side_length = 3.0
beam_width = 0.5
beam_depth = 0.5
beam_height = 15.0
horizontal_width = 0.3
horizontal_depth = 0.3
horizontal_length = 3.0
guywire_radius = 0.05
guywire_length = 10.0
load_cube_size = 0.2
load_mass = 150.0

# Precomputed positions (exact)
sqrt3 = math.sqrt(3.0)
v1_base = (side_length/2, -side_length*sqrt3/6, 0.0)
v2_base = (0.0, side_length*sqrt3/3, 0.0)
v3_base = (-side_length/2, -side_length*sqrt3/6, 0.0)
v1_top = (v1_base[0], v1_base[1], beam_height)
v2_top = (v2_base[0], v2_base[1], beam_height)
v3_top = (v3_base[0], v3_base[1], beam_height)

anchor1 = (5.0, 0.0, 0.0)
anchor2 = (0.0, 5.0, 0.0)
anchor3 = (-5.0, 0.0, 0.0)
centroid = (0.0, 0.0, beam_height)

# ------------------------------------------------------------
# Helper functions
def create_cube(name, location, scale, rigidbody_type='ACTIVE'):
    """Create a cube with rigid body."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigidbody_type
    return obj

def create_cylinder(name, location, radius, length, rigidbody_type='ACTIVE'):
    """Create a cylinder oriented along Z, then rotate to target direction."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=radius,
        depth=1.0,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    # Default cylinder is along Z, height=2 (from -1 to 1). Scale Z to length/2.
    obj.scale = (1.0, 1.0, length / 2.0)
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigidbody_type
    return obj

def align_cylinder(obj, start, end):
    """Rotate cylinder so its local Z points from start to end."""
    start_vec = Vector(start)
    end_vec = Vector(end)
    direction = (end_vec - start_vec).normalized()
    # Default cylinder axis is (0,0,1)
    default_axis = Vector((0, 0, 1))
    rot_axis = default_axis.cross(direction)
    if rot_axis.length > 1e-6:
        rot_axis.normalize()
        angle = default_axis.angle(direction)
        obj.rotation_mode = 'AXIS_ANGLE'
        obj.rotation_axis_angle = (angle, *rot_axis)
    # Move to midpoint
    obj.location = (start_vec + end_vec) / 2.0

def add_fixed_constraint(obj_a, obj_b):
    """Add a FIXED rigid body constraint between two objects."""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj_a
    con.object2 = obj_b

# ------------------------------------------------------------
# 1. Create ground plane (passive)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ------------------------------------------------------------
# 2. Create three vertical beams
vert1 = create_cube(
    "VerticalBeam1",
    (v1_base[0], v1_base[1], beam_height/2.0),
    (beam_width/2.0, beam_depth/2.0, beam_height/2.0),
    'ACTIVE'
)
vert2 = create_cube(
    "VerticalBeam2",
    (v2_base[0], v2_base[1], beam_height/2.0),
    (beam_width/2.0, beam_depth/2.0, beam_height/2.0),
    'ACTIVE'
)
vert3 = create_cube(
    "VerticalBeam3",
    (v3_base[0], v3_base[1], beam_height/2.0),
    (beam_width/2.0, beam_depth/2.0, beam_height/2.0),
    'ACTIVE'
)

# Fix vertical beams to ground
add_fixed_constraint(vert1, ground)
add_fixed_constraint(vert2, ground)
add_fixed_constraint(vert3, ground)

# ------------------------------------------------------------
# 3. Create horizontal connecting beams at top
# Beam between v1 and v2
h12 = create_cube(
    "HorizontalBeam12",
    ((v1_top[0]+v2_top[0])/2, (v1_top[1]+v2_top[1])/2, beam_height),
    (horizontal_width/2.0, horizontal_depth/2.0, horizontal_length/2.0),
    'ACTIVE'
)
# Rotate to align with edge direction
edge = Vector(v2_top) - Vector(v1_top)
angle = math.atan2(edge.y, edge.x)
h12.rotation_euler = (0, 0, angle)

# Beam between v2 and v3
h23 = create_cube(
    "HorizontalBeam23",
    ((v2_top[0]+v3_top[0])/2, (v2_top[1]+v3_top[1])/2, beam_height),
    (horizontal_width/2.0, horizontal_depth/2.0, horizontal_length/2.0),
    'ACTIVE'
)
edge = Vector(v3_top) - Vector(v2_top)
angle = math.atan2(edge.y, edge.x)
h23.rotation_euler = (0, 0, angle)

# Beam between v3 and v1
h31 = create_cube(
    "HorizontalBeam31",
    ((v3_top[0]+v1_top[0])/2, (v3_top[1]+v1_top[1])/2, beam_height),
    (horizontal_width/2.0, horizontal_depth/2.0, horizontal_length/2.0),
    'ACTIVE'
)
edge = Vector(v1_top) - Vector(v3_top)
angle = math.atan2(edge.y, edge.x)
h31.rotation_euler = (0, 0, angle)

# Fix horizontal beams to vertical beams
add_fixed_constraint(h12, vert1)
add_fixed_constraint(h12, vert2)
add_fixed_constraint(h23, vert2)
add_fixed_constraint(h23, vert3)
add_fixed_constraint(h31, vert3)
add_fixed_constraint(h31, vert1)

# ------------------------------------------------------------
# 4. Create anchor points (passive rigid bodies)
anchor_obj1 = create_cube("Anchor1", anchor1, (0.2, 0.2, 0.2), 'PASSIVE')
anchor_obj2 = create_cube("Anchor2", anchor2, (0.2, 0.2, 0.2), 'PASSIVE')
anchor_obj3 = create_cube("Anchor3", anchor3, (0.2, 0.2, 0.2), 'PASSIVE')

# Fix anchors to ground
add_fixed_constraint(anchor_obj1, ground)
add_fixed_constraint(anchor_obj2, ground)
add_fixed_constraint(anchor_obj3, ground)

# ------------------------------------------------------------
# 5. Create guy-wires (cylinders)
# Guy-wire 1: v1_top to anchor1
gw1 = create_cylinder("Guywire1", (0,0,0), guywire_radius, guywire_length, 'ACTIVE')
align_cylinder(gw1, v1_top, anchor1)
# Guy-wire 2: v2_top to anchor2
gw2 = create_cylinder("Guywire2", (0,0,0), guywire_radius, guywire_length, 'ACTIVE')
align_cylinder(gw2, v2_top, anchor2)
# Guy-wire 3: v3_top to anchor3
gw3 = create_cylinder("Guywire3", (0,0,0), guywire_radius, guywire_length, 'ACTIVE')
align_cylinder(gw3, v3_top, anchor3)

# Fix guy-wires to vertical beams and anchors
add_fixed_constraint(gw1, vert1)
add_fixed_constraint(gw1, anchor_obj1)
add_fixed_constraint(gw2, vert2)
add_fixed_constraint(gw2, anchor_obj2)
add_fixed_constraint(gw3, vert3)
add_fixed_constraint(gw3, anchor_obj3)

# ------------------------------------------------------------
# 6. Create top load cube
load_cube = create_cube(
    "TopLoad",
    centroid,
    (load_cube_size/2.0, load_cube_size/2.0, load_cube_size/2.0),
    'ACTIVE'
)
load_cube.rigid_body.mass = load_mass

# Fix load cube to horizontal beams (so it sits on platform)
add_fixed_constraint(load_cube, h12)
add_fixed_constraint(load_cube, h23)
add_fixed_constraint(load_cube, h31)

# ------------------------------------------------------------
# 7. Set up scene for simulation
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Triangular mast with guy-wires constructed successfully.")