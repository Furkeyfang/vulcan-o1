import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
span = 10.0
bottom_chord_size = (10.0, 0.3, 0.3)
bottom_chord_loc = (0.0, 0.0, 0.0)
top_chord_length = 5.5
top_chord_angle = math.radians(26.565)  # Convert to radians
top_chord_cross_section = (top_chord_length, 0.3, 0.3)
apex_height = 2.5
queen_height = 2.0
queen_cross_section = (0.2, 0.2, queen_height)
queen_x_offset = 2.5
strut_length = 2.5
strut_cross_section = (strut_length, 0.2, 0.2)
strut_connection_t = 0.129
load_mass = 1100.0
load_force = 10791.0  # 1100 kg * 9.81 m/s²
apex_sphere_radius = 0.1

# Create Bottom Chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=bottom_chord_loc)
bottom = bpy.context.active_object
bottom.name = "Bottom_Chord"
bottom.scale = bottom_chord_size
bpy.ops.rigidbody.object_add()
bottom.rigid_body.type = 'PASSIVE'

# Create Top Chords (Left and Right)
# Right top chord: from (5,0,0) to (0,0,2.5)
right_top_start = Vector((span/2, 0.0, 0.0))
right_top_end = Vector((0.0, 0.0, apex_height))
right_top_vec = right_top_end - right_top_start
right_top_center = (right_top_start + right_top_end) / 2
right_top_length = right_top_vec.length
right_top_rotation = Vector((0, 1, 0)).rotation_difference(right_top_vec.normalized())

bpy.ops.mesh.primitive_cube_add(size=1.0, location=right_top_center)
right_top = bpy.context.active_object
right_top.name = "Top_Chord_Right"
right_top.scale = (right_top_length, 0.3, 0.3)
right_top.rotation_euler = right_top_rotation.to_euler()
bpy.ops.rigidbody.object_add()
right_top.rigid_body.mass = 100.0

# Left top chord (symmetric)
left_top_start = Vector((-span/2, 0.0, 0.0))
left_top_end = Vector((0.0, 0.0, apex_height))
left_top_vec = left_top_end - left_top_start
left_top_center = (left_top_start + left_top_end) / 2
left_top_length = left_top_vec.length
left_top_rotation = Vector((0, 1, 0)).rotation_difference(left_top_vec.normalized())

bpy.ops.mesh.primitive_cube_add(size=1.0, location=left_top_center)
left_top = bpy.context.active_object
left_top.name = "Top_Chord_Left"
left_top.scale = (left_top_length, 0.3, 0.3)
left_top.rotation_euler = left_top_rotation.to_euler()
bpy.ops.rigidbody.object_add()
left_top.rigid_body.mass = 100.0

# Create Queen Posts
# Right queen post
right_queen_base = Vector((queen_x_offset, 0.0, 0.0))
right_queen_top = Vector((queen_x_offset, 0.0, queen_height))
right_queen_center = (right_queen_base + right_queen_top) / 2

bpy.ops.mesh.primitive_cube_add(size=1.0, location=right_queen_center)
right_queen = bpy.context.active_object
right_queen.name = "Queen_Post_Right"
right_queen.scale = queen_cross_section
bpy.ops.rigidbody.object_add()
right_queen.rigid_body.mass = 50.0

# Left queen post
left_queen_base = Vector((-queen_x_offset, 0.0, 0.0))
left_queen_top = Vector((-queen_x_offset, 0.0, queen_height))
left_queen_center = (left_queen_base + left_queen_top) / 2

bpy.ops.mesh.primitive_cube_add(size=1.0, location=left_queen_center)
left_queen = bpy.context.active_object
left_queen.name = "Queen_Post_Left"
left_queen.scale = queen_cross_section
bpy.ops.rigidbody.object_add()
left_queen.rigid_body.mass = 50.0

# Create Struts
# Right strut: from queen top to point on top chord
right_strut_start = Vector((queen_x_offset, 0.0, queen_height))
# Point on right top chord at parameter t
right_strut_end = Vector((
    span/2 * (1 - strut_connection_t),
    0.0,
    apex_height * strut_connection_t
))
right_strut_vec = right_strut_end - right_strut_start
right_strut_center = (right_strut_start + right_strut_end) / 2
right_strut_length = right_strut_vec.length
right_strut_rotation = Vector((0, 1, 0)).rotation_difference(right_strut_vec.normalized())

bpy.ops.mesh.primitive_cube_add(size=1.0, location=right_strut_center)
right_strut = bpy.context.active_object
right_strut.name = "Strut_Right"
right_strut.scale = (right_strut_length, 0.2, 0.2)
right_strut.rotation_euler = right_strut_rotation.to_euler()
bpy.ops.rigidbody.object_add()
right_strut.rigid_body.mass = 30.0

# Left strut (symmetric)
left_strut_start = Vector((-queen_x_offset, 0.0, queen_height))
left_strut_end = Vector((
    -span/2 * (1 - strut_connection_t),
    0.0,
    apex_height * strut_connection_t
))
left_strut_vec = left_strut_end - left_strut_start
left_strut_center = (left_strut_start + left_strut_end) / 2
left_strut_length = left_strut_vec.length
left_strut_rotation = Vector((0, 1, 0)).rotation_difference(left_strut_vec.normalized())

bpy.ops.mesh.primitive_cube_add(size=1.0, location=left_strut_center)
left_strut = bpy.context.active_object
left_strut.name = "Strut_Left"
left_strut.scale = (left_strut_length, 0.2, 0.2)
left_strut.rotation_euler = left_strut_rotation.to_euler()
bpy.ops.rigidbody.object_add()
left_strut.rigid_body.mass = 30.0

# Create Apex Sphere for Load Application
bpy.ops.mesh.primitive_uv_sphere_add(radius=apex_sphere_radius, location=(0.0, 0.0, apex_height))
apex = bpy.context.active_object
apex.name = "Apex_Load"
bpy.ops.rigidbody.object_add()
apex.rigid_body.mass = load_mass

# Apply downward force (gravity will handle this, but we add extra force for the load)
# In Blender, forces are applied per frame. We'll use a constant force constraint.
bpy.ops.object.empty_add(type='ARROWS', location=(0.0, 0.0, apex_height))
force_empty = bpy.context.active_object
force_empty.name = "Force_Application"

# Create force field
bpy.ops.object.effector_add(type='FORCE', location=(0.0, 0.0, apex_height))
force_field = bpy.context.active_object
force_field.name = "Downward_Force"
force_field.field.strength = -load_force
force_field.field.falloff_power = 0
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.2

# Parent force field to apex sphere
force_field.parent = apex

# Create FIXED Constraints (Rigid Joints)
def create_fixed_constraint(obj1, obj2, location):
    """Create a FIXED rigid body constraint between two objects"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Fixed_{obj1.name}_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Bottom chord to top chords
create_fixed_constraint(bottom, right_top, (span/2, 0.0, 0.0))
create_fixed_constraint(bottom, left_top, (-span/2, 0.0, 0.0))

# Bottom chord to queen posts
create_fixed_constraint(bottom, right_queen, (queen_x_offset, 0.0, 0.0))
create_fixed_constraint(bottom, left_queen, (-queen_x_offset, 0.0, 0.0))

# Top chords to apex sphere
create_fixed_constraint(right_top, apex, (0.0, 0.0, apex_height))
create_fixed_constraint(left_top, apex, (0.0, 0.0, apex_height))

# Queen posts to struts
create_fixed_constraint(right_queen, right_strut, (queen_x_offset, 0.0, queen_height))
create_fixed_constraint(left_queen, left_strut, (-queen_x_offset, 0.0, queen_height))

# Struts to top chords
create_fixed_constraint(right_strut, right_top, tuple(right_strut_end))
create_fixed_constraint(left_strut, left_top, tuple(left_strut_end))

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 250  # Run simulation for 250 frames

print("Truss construction complete. All joints are FIXED.")
print(f"Central load: {load_mass} kg ({load_force} N) applied at apex.")