import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ============================================
# Parameters from summary
# ============================================
# Locations
apex_loc = (0.0, 0.0, 5.0)
support_L_loc = (-10.0, 0.0, 0.0)
support_R_loc = (10.0, 0.0, 0.0)
queen_post_top_L = (-5.0, 0.0, 2.5)
queen_post_bottom_L = (-5.0, 0.0, 0.0)
queen_post_top_R = (5.0, 0.0, 2.5)
queen_post_bottom_R = (5.0, 0.0, 0.0)

# Dimensions
cross_section = 0.3
rafter_L_length = 11.1803398875
rafter_R_length = 11.1803398875
queen_post_height = 2.5
tie_beam_length = 20.0

# Physics
load_force = 21582.0
gravity = 9.81
damping_linear = 0.5
damping_angular = 0.5

# ============================================
# Utility functions
# ============================================
def create_beam(name, length, cross, location, rotation):
    """Create a cuboid beam with given length and square cross-section."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    # Scale: default cube is 2x2x2, so scale = desired_length / 2
    obj.scale = (cross / 2, cross / 2, length / 2)
    obj.rotation_euler = rotation
    # Apply scale to avoid distortion in physics
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    """Add rigid body properties."""
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.linear_damping = damping_linear
    obj.rigid_body.angular_damping = damping_angular

def add_fixed_constraint(obj_a, obj_b):
    """Add a fixed constraint between two objects."""
    # Select obj_a then obj_b, then add constraint
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    obj_b.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = bpy.context.active_object
    const.rigid_body_constraint.type = 'FIXED'

# ============================================
# Create members
# ============================================
# Left rafter (from apex to left support)
rafter_L_mid = Vector(apex_loc).lerp(Vector(support_L_loc), 0.5)
rafter_L_dir = Vector(support_L_loc) - Vector(apex_loc)
rafter_L_rot = Vector((0,0,1)).rotation_difference(rafter_L_dir).to_euler()
rafter_L = create_beam("Rafter_L", rafter_L_length, cross_section,
                       rafter_L_mid, rafter_L_rot)
add_rigidbody(rafter_L)

# Right rafter (from apex to right support)
rafter_R_mid = Vector(apex_loc).lerp(Vector(support_R_loc), 0.5)
rafter_R_dir = Vector(support_R_loc) - Vector(apex_loc)
rafter_R_rot = Vector((0,0,1)).rotation_difference(rafter_R_dir).to_euler()
rafter_R = create_beam("Rafter_R", rafter_R_length, cross_section,
                       rafter_R_mid, rafter_R_rot)
add_rigidbody(rafter_R)

# Left queen post (vertical)
queen_L_mid = Vector(queen_post_bottom_L).lerp(Vector(queen_post_top_L), 0.5)
queen_L = create_beam("QueenPost_L", queen_post_height, cross_section,
                      queen_L_mid, (0,0,0))
add_rigidbody(queen_L)

# Right queen post (vertical)
queen_R_mid = Vector(queen_post_bottom_R).lerp(Vector(queen_post_top_R), 0.5)
queen_R = create_beam("QueenPost_R", queen_post_height, cross_section,
                      queen_R_mid, (0,0,0))
add_rigidbody(queen_R)

# Tie beam (horizontal)
tie_mid = Vector((0,0,0))
tie = create_beam("TieBeam", tie_beam_length, cross_section,
                  tie_mid, (0,0,0))
add_rigidbody(tie, mass=100.0)  # Slightly higher mass for stability

# Supports (passive)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_L_loc)
support_L = bpy.context.active_object
support_L.name = "Support_L"
support_L.scale = (0.5, 0.5, 0.2)
add_rigidbody(support_L, 'PASSIVE')

bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_R_loc)
support_R = bpy.context.active_object
support_R.name = "Support_R"
support_R.scale = (0.5, 0.5, 0.2)
add_rigidbody(support_R, 'PASSIVE')

# Apex joint (small passive cube to connect rafters)
bpy.ops.mesh.primitive_cube_add(size=0.2, location=apex_loc)
apex_joint = bpy.context.active_object
apex_joint.name = "ApexJoint"
add_rigidbody(apex_joint, 'PASSIVE')

# ============================================
# Add fixed constraints
# ============================================
# Apex: connect both rafters to apex joint
add_fixed_constraint(rafter_L, apex_joint)
add_fixed_constraint(rafter_R, apex_joint)

# Left queen post: connect to rafter (at top) and tie beam (at bottom)
add_fixed_constraint(queen_L, rafter_L)
add_fixed_constraint(queen_L, tie)

# Right queen post: connect to rafter and tie beam
add_fixed_constraint(queen_R, rafter_R)
add_fixed_constraint(queen_R, tie)

# Tie beam to supports
add_fixed_constraint(tie, support_L)
add_fixed_constraint(tie, support_R)

# ============================================
# Apply load as a force field
# ============================================
# Create a force field (empty) at the tie beam center
bpy.ops.object.empty_add(type='PLAIN_AXES', location=tie_mid)
force_empty = bpy.context.active_object
force_empty.name = "LoadForce"
bpy.ops.object.forcefield_toggle()
field = force_empty.field
field.type = 'FORCE'
field.strength = -load_force  # Negative Z direction
field.direction = 'Z'
field.use_max_distance = True
field.max_distance = tie_beam_length / 2  # Cover the tie beam
field.falloff_power = 0  # Uniform

# Limit force field to affect only the tie beam
# Create a collection for the tie beam and assign
load_collection = bpy.data.collections.new("LoadCollection")
bpy.context.scene.collection.children.link(load_collection)
load_collection.objects.link(tie)
force_empty.field.override_collection = load_collection

# ============================================
# Adjust world physics
# ============================================
bpy.context.scene.gravity = (0, 0, -gravity)
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Queen Post truss assembly complete. Load applied.")