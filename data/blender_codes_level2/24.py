import bpy
import mathutils
from math import sqrt, radians

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span_x = 3.0
beam_cross = 0.1
v_height = 3.0
diag_len = sqrt(span_x**2 + v_height**2)
load_force = 2943.0

# Vertex coordinates
left_anchor = (0.0, 0.0, 0.0)
right_anchor = (span_x, 0.0, 0.0)
top_vertex = (0.0, 0.0, v_height)

# Beam centers
top_center = (span_x/2, 0.0, v_height)
vertical_center = (0.0, 0.0, v_height/2)
diagonal_center = (span_x/2, 0.0, v_height/2)

# Force application
force_point = (span_x/2, 0.0, v_height)

# Helper function to create beam
def create_beam(name, location, length, rotation_euler):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (length, beam_cross, beam_cross)
    beam.rotation_euler = rotation_euler
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.mass = length * beam_cross * beam_cross * 100.0  # Density based
    beam.rigid_body.collision_shape = 'BOX'
    
    return beam

# Create top beam (horizontal)
top_beam = create_beam(
    "TopBeam",
    top_center,
    span_x,
    (0.0, 0.0, 0.0)
)

# Create vertical beam
vertical_beam = create_beam(
    "VerticalBeam",
    vertical_center,
    v_height,
    (0.0, 0.0, 0.0)
)

# Create diagonal beam
diagonal_beam = create_beam(
    "DiagonalBeam",
    diagonal_center,
    diag_len,
    (0.0, radians(-45), 0.0)  # Rotate -45° around Y-axis
)

# Create anchor points (passive rigid bodies)
def create_anchor(name, location):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=location)
    anchor = bpy.context.active_object
    anchor.name = name
    bpy.ops.rigidbody.object_add()
    anchor.rigid_body.type = 'PASSIVE'
    return anchor

left_anchor_obj = create_anchor("LeftAnchor", left_anchor)
right_anchor_obj = create_anchor("RightAnchor", right_anchor)

# Apply fixed constraints between beams
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.constraints[-1]
    constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    constraint.type = 'FIXED'
    constraint.object2 = obj_b

# Connect beams at vertices
add_fixed_constraint(top_beam, vertical_beam)          # Top-left vertex
add_fixed_constraint(top_beam, diagonal_beam)          # Top-right via diagonal
add_fixed_constraint(vertical_beam, diagonal_beam)     # Bottom-left vertex
add_fixed_constraint(vertical_beam, left_anchor_obj)   # Ground left
add_fixed_constraint(diagonal_beam, right_anchor_obj)  # Ground right

# Apply downward force at top beam midpoint
bpy.context.view_layer.objects.active = top_beam
top_beam.rigid_body.use_gravity = True

# Create force application object
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.05, location=force_point)
force_applier = bpy.context.active_object
force_applier.name = "ForceApplier"
force_applier.hide_render = True
bpy.ops.rigidbody.object_add()
force_applier.rigid_body.type = 'ACTIVE'
force_applier.rigid_body.mass = 300.0  # 300 kg

# Add fixed constraint to apply force
bpy.ops.rigidbody.constraint_add()
force_constraint = top_beam.constraints[-1]
force_constraint.name = "LoadConstraint"
force_constraint.type = 'GENERIC_SPRING'
force_constraint.object2 = force_applier
force_constraint.use_spring_x = True
force_constraint.use_spring_y = True
force_constraint.use_spring_z = True
force_constraint.spring_stiffness_z = 0.0  # Allow vertical movement
force_constraint.spring_damping_z = 100.0

# Apply initial downward impulse
force_applier.rigid_body.apply_force([0, 0, -load_force])

# Set up physics world
bpy.context.scene.rigidbody_world.steps_per_second = 240
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 250

print("Triangular truss constructed with fixed joints and 300kg load applied.")