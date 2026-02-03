import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Variables from summary
col_rad = 0.3
col_h = 7.0
col_center = (0.0, 0.0, 3.5)
arm_dim = (2.0, 0.3, 0.3)
arm_center = (1.0, 0.0, 7.0)
fl_dim = (0.8, 0.8, 0.5)
fl_center = (2.4, 0.0, 7.0)
fl_mass = 120.0
steel_density = 7850.0

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Column (Cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=col_rad, depth=col_h, location=col_center)
column = bpy.context.active_object
column.name = "Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'  # Fixed to ground
# Calculate mass from volume: πr²h
col_vol = math.pi * col_rad**2 * col_h
column.rigid_body.mass = col_vol * steel_density

# Create Arm (Cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_center)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim  # Scale to dimensions
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
# Mass from volume
arm_vol = arm_dim[0] * arm_dim[1] * arm_dim[2]
arm.rigid_body.mass = arm_vol * steel_density

# Create Floodlight (Cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=fl_center)
floodlight = bpy.context.active_object
floodlight.name = "Floodlight"
floodlight.scale = fl_dim
bpy.ops.rigidbody.object_add()
floodlight.rigid_body.type = 'ACTIVE'
floodlight.rigid_body.mass = fl_mass

# Create Hinge Constraint between Column and Arm
# Add empty at hinge location (column top)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 7.0))
hinge = bpy.context.active_object
hinge.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge.rigid_body_constraint.type = 'HINGE'
# Set constraint to connect column and arm
hinge.rigid_body_constraint.object1 = column
hinge.rigid_body_constraint.object2 = arm
# Hinge axis: Y (for vertical rotation)
hinge.rigid_body_constraint.use_angular_x = False
hinge.rigid_body_constraint.use_angular_y = True
hinge.rigid_body_constraint.use_angular_z = False

# Create Fixed Constraint between Arm and Floodlight
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(2.0, 0.0, 7.0))
fixed = bpy.context.active_object
fixed.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
fixed.rigid_body_constraint.type = 'FIXED'
fixed.rigid_body_constraint.object1 = arm
fixed.rigid_body_constraint.object2 = floodlight

# Set simulation parameters for verification
scene = bpy.context.scene
scene.frame_end = 100  # Simulate 100 frames
scene.rigidbody_world.substeps_per_frame = 10
scene.rigidbody_world.solver_iterations = 50

# Optional: Bake simulation for headless verification
# bpy.ops.ptcache.bake_all(bake=True)