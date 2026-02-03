import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Variables from summary
column_dim = (0.5, 0.5, 15.0)
column_loc = (0.0, 0.0, 7.5)
beam_dim = (15.0, 0.5, 0.5)
beam_loc = (7.5, 0.0, 15.0)
brace_dim = (0.3, 0.3, 21.2132)
brace_loc = (7.5, 0.0, 7.5)
brace_rot_y = -45.0
load_dim = (1.0, 1.0, 1.0)
load_loc = (7.5, 0.0, 15.75)
load_mass = 1000.0
anchor_base_loc = (0.0, 0.0, 0.0)
anchor_brace_loc = (15.0, 0.0, 0.0)
joint_top_loc = (0.0, 0.0, 15.0)

# Helper to add rigid body
def add_rigidbody(obj, rb_type='PASSIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.mass = mass

# Create Column
bpy.ops.mesh.primitive_cube_add(size=1, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
add_rigidbody(column, 'PASSIVE')

# Create Horizontal Beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Horizontal_Beam"
beam.scale = beam_dim
add_rigidbody(beam, 'PASSIVE')

# Create Diagonal Brace
bpy.ops.mesh.primitive_cube_add(size=1, location=brace_loc)
brace = bpy.context.active_object
brace.name = "Diagonal_Brace"
brace.scale = brace_dim
brace.rotation_euler = (0, math.radians(brace_rot_y), 0)
add_rigidbody(brace, 'PASSIVE')

# Create Load
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
add_rigidbody(load, 'ACTIVE', load_mass)

# Create Ground Anchors (Empties with rigid bodies)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=anchor_base_loc)
anchor_base = bpy.context.active_object
anchor_base.name = "Anchor_Base"
add_rigidbody(anchor_base, 'PASSIVE')

bpy.ops.object.empty_add(type='PLAIN_AXES', location=anchor_brace_loc)
anchor_brace = bpy.context.active_object
anchor_brace.name = "Anchor_Brace"
add_rigidbody(anchor_brace, 'PASSIVE')

# Create Top Joint (Empty)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=joint_top_loc)
joint_top = bpy.context.active_object
joint_top.name = "Joint_Top"
add_rigidbody(joint_top, 'PASSIVE')

# Create Fixed Constraints
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b

# Apply all constraints
add_fixed_constraint(anchor_base, column)      # Base anchor to column
add_fixed_constraint(joint_top, column)        # Top joint to column
add_fixed_constraint(joint_top, beam)          # Top joint to beam
add_fixed_constraint(joint_top, brace)         # Top joint to brace
add_fixed_constraint(anchor_brace, brace)      # Brace anchor to brace
add_fixed_constraint(beam, load)               # Beam to load

# Set gravity (default is -9.81 Z)
bpy.context.scene.gravity = (0, 0, -9.81)

# Ensure proper collision margins
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

print("Structural frame with gravity load path created.")