import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_base = (0.0, 0.0, 0.0)
col_size = (0.5, 0.5, 2.0)
col_loc = (0.0, 0.0, 1.0)
arm_size = (3.0, 0.2, 0.2)
arm_loc = (1.5, 0.0, 2.0)
load_size = (0.5, 0.5, 0.5)
load_loc = (3.0, 0.0, 2.0)
load_mass = 150.0
arm_mass = 10.0
sim_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
col = bpy.context.active_object
col.scale = col_size
col.name = "Support_Column"
bpy.ops.rigidbody.object_add()
col.rigid_body.type = 'PASSIVE'  # Fixed to ground
col.rigid_body.collision_shape = 'BOX'

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.scale = arm_size
arm.name = "Arm"
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass
arm.rigid_body.collision_shape = 'BOX'

# Create Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.scale = load_size
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraint between Column and Arm
# In headless mode, we create an empty with constraint properties
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,2))
constraint1 = bpy.context.active_object
constraint1.name = "Col_Arm_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = col
constraint1.rigid_body_constraint.object2 = arm

# Create Fixed Constraint between Arm and Load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(3,0,2))
constraint2 = bpy.context.active_object
constraint2.name = "Arm_Load_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = arm
constraint2.rigid_body_constraint.object2 = load

# Set simulation end frame
bpy.context.scene.frame_end = sim_frames

# Optional: run simulation by setting frame (headless requires manual stepping)
# For verification, we can bake the simulation, but in headless we rely on Blender's physics
# Simple advancement:
for frame in range(1, sim_frames+1):
    bpy.context.scene.frame_set(frame)
    # In headless, physics auto-updates if we have a rigid body world
    # We can print positions for debugging (optional)
    # print(f"Frame {frame}: Load at {load.location}")