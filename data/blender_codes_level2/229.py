import bpy
import mathutils
from mathutils import Vector

# ------------------------------------------------------------
# 1. Clear existing scene
# ------------------------------------------------------------
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ------------------------------------------------------------
# 2. Define parameters from summary
# ------------------------------------------------------------
side_length = 8.0
triangle_height = side_length * 0.866025404  # sqrt(3)/2
member_thickness = 0.2
median_length = triangle_height
inner_length = side_length / 2.0

vertex_A = Vector((-side_length/2.0, -triangle_height/3.0, 0.0))
vertex_B = Vector((side_length/2.0, -triangle_height/3.0, 0.0))
vertex_C = Vector((0.0, 2.0*triangle_height/3.0, 0.0))

midpoint_D = (vertex_B + vertex_C) / 2.0
midpoint_E = (vertex_A + vertex_C) / 2.0
midpoint_F = (vertex_A + vertex_B) / 2.0

column_radius = 0.3
column_height = 3.0
column_top_z = 0.0
column_base_z = -column_height

load_size = (1.0, 1.0, 0.1)
load_loc = Vector((0.0, 0.0, 0.1))
load_mass = 900.0

# ------------------------------------------------------------
# 3. Function to create a beam between two points
# ------------------------------------------------------------
def create_beam(point1, point2, thickness, name):
    """Create a cube beam from point1 to point2 with given thickness."""
    direction = point2 - point1
    length = direction.length
    center = (point1 + point2) / 2.0
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    beam = bpy.context.active_object
    beam.name = name
    # Scale: thickness in X/Y, length in Z (local)
    beam.scale = (thickness/2.0, thickness/2.0, length/2.0)
    
    # Rotate to align local Z with direction
    if length > 1e-6:
        z_axis = Vector((0,0,1))
        rot_quat = z_axis.rotation_difference(direction)
        beam.rotation_mode = 'QUATERNION'
        beam.rotation_quaternion = rot_quat
    
    return beam

# ------------------------------------------------------------
# 4. Create base grid (edges of triangle)
# ------------------------------------------------------------
base_AB = create_beam(vertex_A, vertex_B, member_thickness, "Base_AB")
base_BC = create_beam(vertex_B, vertex_C, member_thickness, "Base_BC")
base_CA = create_beam(vertex_C, vertex_A, member_thickness, "Base_CA")

# ------------------------------------------------------------
# 5. Create internal grid (medians and inner triangle)
# ------------------------------------------------------------
median_AD = create_beam(vertex_A, midpoint_D, member_thickness, "Median_AD")
median_BE = create_beam(vertex_B, midpoint_E, member_thickness, "Median_BE")
median_CF = create_beam(vertex_C, midpoint_F, member_thickness, "Median_CF")

inner_DE = create_beam(midpoint_D, midpoint_E, member_thickness, "Inner_DE")
inner_EF = create_beam(midpoint_E, midpoint_F, member_thickness, "Inner_EF")
inner_FD = create_beam(midpoint_F, midpoint_D, member_thickness, "Inner_FD")

# ------------------------------------------------------------
# 6. Create support columns (vertical cylinders at vertices)
# ------------------------------------------------------------
def create_column(location, radius, height, name):
    """Create a vertical cylinder column with base at ground."""
    # Cylinder default: radius=1, depth=2, aligned along local Z
    # We scale radius and depth, then position so top at vertex, base at ground
    top = Vector(location)
    base = Vector((location.x, location.y, column_base_z))
    center = (top + base) / 2.0
    actual_height = top.z - base.z
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=1.0,
        depth=2.0,
        location=center
    )
    col = bpy.context.active_object
    col.name = name
    # Scale: radius in X/Y, height in Z (depth)
    col.scale = (radius, radius, actual_height/2.0)
    # No rotation needed (already Z‑aligned)
    return col

col_A = create_column(vertex_A, column_radius, column_height, "Column_A")
col_B = create_column(vertex_B, column_radius, column_height, "Column_B")
col_C = create_column(vertex_C, column_radius, column_height, "Column_C")

# ------------------------------------------------------------
# 7. Create load cube
# ------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size[0]/2.0, load_size[1]/2.0, load_size[2]/2.0)

# ------------------------------------------------------------
# 8. Assign rigid body properties
# ------------------------------------------------------------
# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# All structural elements: passive
structure_objects = [
    base_AB, base_BC, base_CA,
    median_AD, median_BE, median_CF,
    inner_DE, inner_EF, inner_FD,
    col_A, col_B, col_C
]

for obj in structure_objects:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    obj.rigid_body.collision_shape = 'CONVEX_HULL'

# Load: active with mass
bpy.context.view_layer.objects.active = load
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Set gravity (default is 9.81, but explicit)
bpy.context.scene.gravity = (0, 0, -9.81)

# ------------------------------------------------------------
# 9. Create fixed constraints at all junctions
# ------------------------------------------------------------
def add_fixed_constraint(obj1, obj2):
    """Add a FIXED rigid body constraint between obj1 and obj2."""
    # Create empty object for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    const = bpy.context.active_object
    const.name = f"Fix_{obj1.name}_{obj2.name}"
    const.location = (obj1.location + obj2.location) / 2.0
    
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = obj1
    const.rigid_body_constraint.object2 = obj2

# Junctions at vertices
add_fixed_constraint(base_AB, base_CA)  # at A
add_fixed_constraint(base_AB, base_BC)  # at B
add_fixed_constraint(base_BC, base_CA)  # at C

add_fixed_constraint(base_AB, median_AD)  # A: base & median
add_fixed_constraint(base_CA, median_AD)
add_fixed_constraint(base_AB, median_BE)  # B
add_fixed_constraint(base_BC, median_BE)
add_fixed_constraint(base_BC, median_CF)  # C
add_fixed_constraint(base_CA, median_CF)

add_fixed_constraint(median_AD, col_A)  # columns
add_fixed_constraint(median_BE, col_B)
add_fixed_constraint(median_CF, col_C)

# Junctions at midpoints
add_fixed_constraint(median_AD, inner_DE)  # D
add_fixed_constraint(median_AD, inner_FD)
add_fixed_constraint(inner_DE, inner_FD)

add_fixed_constraint(median_BE, inner_DE)  # E
add_fixed_constraint(median_BE, inner_EF)
add_fixed_constraint(inner_DE, inner_EF)

add_fixed_constraint(median_CF, inner_EF)  # F
add_fixed_constraint(median_CF, inner_FD)
add_fixed_constraint(inner_EF, inner_FD)

# ------------------------------------------------------------
# 10. Final scene settings
# ------------------------------------------------------------
bpy.context.scene.frame_end = 100  # simulate 100 frames
print("Triangular space grid roof constructed. Ready for simulation.")