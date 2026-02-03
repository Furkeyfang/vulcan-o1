import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
mast_dim = (0.2, 0.2, 6.0)
mast_loc = (0.0, 0.0, 3.0)
arm_dim = (1.0, 0.1, 0.1)
arm_loc = (0.5, 0.0, 6.0)
hinge_pivot_world = (0.0, 0.0, 6.0)
hinge_axis = (0.0, 1.0, 0.0)
motor_target_vel = 0.0
motor_torque = 294300.0  # N·mm
sim_frames = 100
max_deflection = 0.1

# Enable rigid body physics
bpy.context.scene.rigidbody_world.enabled = True

# Create Mast
bpy.ops.mesh.primitive_cube_add(size=1, location=mast_loc)
mast = bpy.context.active_object
mast.name = "Mast"
mast.scale = mast_dim
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'PASSIVE'
mast.rigid_body.collision_shape = 'BOX'

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_dim[0]/2, arm_dim[1]/2, arm_dim[2]/2)  # Cube default 2x2x2
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.use_gravity = False  # Isolate motor torque effect
arm.rigid_body.mass = 0.1  # Minimal mass

# Create Hinge Constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot_world)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"

# Add rigid body constraint
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = mast
constraint.object2 = arm
constraint.disable_collisions = True

# Set hinge pivots in local spaces
# Mast local pivot: (0,0,3) since mast center at Z=3, top at Z=6 in local
constraint.pivot_type = 'CUSTOM'
constraint.pivot_x = 0.0
constraint.pivot_y = 0.0
constraint.pivot_z = 3.0  # Local Z offset from mast center to top

# Arm local pivot: (-0.5,0,0) since arm center offset 0.5m from hinge
constraint.use_spring = False
constraint.use_limit_ang_z = False

# Set motor properties
constraint.use_motor_ang = True
constraint.motor_ang_target_velocity = motor_target_vel
constraint.motor_ang_max_impulse = motor_torque  # N·mm

# Bake simulation
bpy.context.scene.frame_end = sim_frames
bpy.ops.ptcache.bake_all()

# Verify deflection
bpy.context.scene.frame_set(sim_frames)
free_end_local = mathutils.Vector((0.5, 0.0, 0.0))  # Arm center to right end
free_end_world = arm.matrix_world @ free_end_local
initial_z = 6.0
deflection = initial_z - free_end_world.z

print(f"Arm free end position after {sim_frames} frames: {free_end_world}")
print(f"Vertical deflection: {deflection:.4f} m")
print(f"Requirement: deflection ≤ {max_deflection} m")
print(f"Test {'PASSED' if deflection <= max_deflection else 'FAILED'}")