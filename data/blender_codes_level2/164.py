import bpy
import mathutils
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
col_dim = Vector((0.5, 0.5, 14.0))
col_center = Vector((0.0, 0.0, 7.0))
brace_cross = 0.3
brace_local_len = 2.0
brace_vecs = [Vector((2,2,2)), Vector((2,-2,2)), Vector((-2,2,2)), Vector((-2,-2,2))]
force_mag = -17658.0
force_loc = Vector((0.0, 0.0, 14.0))
ground_size = 10.0
density = 7850.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create primary column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_center)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.mass = density * (col_dim.x * col_dim.y * col_dim.z)

# Create bracing members
braces = []
for vec in brace_vecs:
    # Calculate midpoint
    midpoint = vec / 2
    # Create brace cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
    brace = bpy.context.active_object
    brace.name = f"Brace_{vec}"
    
    # Scale cross-section and initial length
    brace.scale = (brace_cross, brace_cross, brace_local_len)
    
    # Calculate rotation to align local Z with vector
    vec_normalized = vec.normalized()
    up = Vector((0, 0, 1))
    rot_quat = up.rotation_difference(vec_normalized)
    brace.rotation_mode = 'QUATERNION'
    brace.rotation_quaternion = rot_quat
    
    # Scale length to match vector magnitude
    target_length = vec.length
    scale_factor = target_length / brace_local_len
    # Apply scale in local Z direction
    mat = brace.matrix_world
    local_z = mat.to_3x3() @ Vector((0, 0, 1))
    brace.scale = brace.scale * Vector((1, 1, scale_factor))
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    brace_volume = brace_cross**2 * target_length
    brace.rigid_body.mass = density * brace_volume
    
    braces.append(brace)

# Create fixed constraints between column and braces
for i, brace in enumerate(braces):
    vec = brace_vecs[i]
    
    # Constraint at base (0,0,0)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty_base = bpy.context.active_object
    empty_base.name = f"Constraint_Base_{i}"
    bpy.ops.rigidbody.constraint_add()
    constraint_base = empty_base.rigid_body_constraint
    constraint_base.type = 'FIXED'
    constraint_base.object1 = column
    constraint_base.object2 = brace
    
    # Constraint at upper point (vec)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=vec)
    empty_upper = bpy.context.active_object
    empty_upper.name = f"Constraint_Upper_{i}"
    bpy.ops.rigidbody.constraint_add()
    constraint_upper = empty_upper.rigid_body_constraint
    constraint_upper.type = 'FIXED'
    constraint_upper.object1 = column
    constraint_upper.object2 = brace

# Create force field at top of column
bpy.ops.object.empty_add(type='SPHERE', location=force_loc)
force_empty = bpy.context.active_object
force_empty.name = "Force_Field"
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = force_mag
force_empty.field.direction = 'Z'
force_empty.field.use_absorption = True
force_empty.field.falloff_power = 0

# Set physics scene properties
scene = bpy.context.scene
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50
scene.rigidbody_world.use_split_impulse = True

print("Truss construction complete. Simulation ready.")