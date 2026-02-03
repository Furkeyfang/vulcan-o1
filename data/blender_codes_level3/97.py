import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
p_dim = (3.0, 2.0, 0.5)
p_loc = (0.0, 0.0, 0.25)
s_dim = (2.0, 1.5, 0.4)
s_loc = (0.0, 1.75, 0.25)
hinge_piv = (0.0, 1.0, 0.25)
hinge_ax = (0.0, 0.0, 1.0)
motor_vel = 2.0
g_loc = (0.0, 0.0, 0.0)

# Create primary chassis (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=p_loc)
primary = bpy.context.active_object
primary.scale = p_dim
primary.name = "Primary_Chassis"
bpy.ops.rigidbody.object_add()
primary.rigid_body.type = 'ACTIVE'  # Will be constrained to ground

# Create secondary body (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=s_loc)
secondary = bpy.context.active_object
secondary.scale = s_dim
secondary.name = "Secondary_Body"
bpy.ops.rigidbody.object_add()
secondary.rigid_body.type = 'ACTIVE'

# Create ground empty (passive anchor)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=g_loc)
ground_empty = bpy.context.active_object
ground_empty.name = "Ground_Empty"
bpy.ops.rigidbody.object_add()
ground_empty.rigid_body.type = 'PASSIVE'

# Add fixed constraint between primary and ground
bpy.ops.object.constraint_add(type='FIXED')
primary.constraints["Fixed"].target = ground_empty

# Add hinge constraint between primary and secondary
bpy.ops.object.constraint_add(type='HINGE')
hinge_constraint = secondary.constraints["Hinge"]
hinge_constraint.target = primary
hinge_constraint.pivot_type = 'CUSTOM'
hinge_constraint.hinge_axis = 'Z'
# Set custom pivot in world coordinates
hinge_constraint.use_custom_space = True
hinge_constraint.space_object = None  # World space
secondary.matrix_world = mathutils.Matrix.Translation(s_loc)
# Manually set pivot location (requires setting the constraint's offset)
hinge_constraint.own_space = 'CUSTOM'
hinge_constraint.target_space = 'CUSTOM'
# Create an empty at pivot for own space
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_piv)
pivot_empty = bpy.context.active_object
pivot_empty.name = "Hinge_Pivot_Empty"
hinge_constraint.own_space_object = pivot_empty
hinge_constraint.target_space_object = pivot_empty
# Alternatively, set pivot directly via Python API (simpler):
hinge_constraint.pivot_x = hinge_piv[0]
hinge_constraint.pivot_y = hinge_piv[1]
hinge_constraint.pivot_z = hinge_piv[2]
# Enable motor
hinge_constraint.use_motor = True
hinge_constraint.motor_velocity = motor_vel

# Set collision shapes (box for both)
primary.rigid_body.collision_shape = 'BOX'
secondary.rigid_body.collision_shape = 'BOX'

# Ensure rigid body world is enabled
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Optional: Set simulation steps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Articulated rover construction complete. Primary fixed, hinge motor activated.")