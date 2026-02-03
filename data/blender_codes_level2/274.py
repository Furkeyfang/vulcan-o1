import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
cube_dim = (1.0, 1.0, 1.0)
num_levels = 18
total_height = 18.0
rotation_increment = 10.0
load_dim = (0.5, 0.5, 0.5)
load_mass = 300.0
load_z = 18.75
constraint_type = 'FIXED'

# Create tower levels
previous_cube = None
for i in range(num_levels):
    # Calculate position and rotation
    height_z = i * cube_dim[2]  # Each cube sits exactly above previous
    rotation_z = math.radians(i * rotation_increment)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, height_z))
    cube = bpy.context.active_object
    cube.scale = cube_dim
    cube.rotation_euler = (0, 0, rotation_z)
    
    # Add rigid body physics (passive for tower)
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.type = 'PASSIVE'
    
    # Create fixed constraint to previous cube (except for base)
    if previous_cube:
        # Select previous cube first (parent)
        bpy.ops.object.select_all(action='DESELECT')
        previous_cube.select_set(True)
        bpy.context.view_layer.objects.active = previous_cube
        
        # Add constraint
        bpy.ops.rigidbody.constraint_add()
        constraint = bpy.context.active_object
        constraint.rigid_body_constraint.type = constraint_type
        constraint.rigid_body_constraint.object1 = previous_cube
        constraint.rigid_body_constraint.object2 = cube
    
    previous_cube = cube

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, load_z))
load = bpy.context.active_object
load.scale = load_dim
load.rotation_euler = (0, 0, math.radians((num_levels - 1) * rotation_increment))

# Add rigid body physics for load (active with mass)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Constrain load to top tower cube
if previous_cube:
    bpy.ops.object.select_all(action='DESELECT')
    previous_cube.select_set(True)
    bpy.context.view_layer.objects.active = previous_cube
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.rigid_body_constraint.type = constraint_type
    constraint.rigid_body_constraint.object1 = previous_cube
    constraint.rigid_body_constraint.object2 = load

# Set world physics properties (default gravity -9.81 in Z)
bpy.context.scene.rigidbody_world.enabled = True

# Optional: Set simulation end frame to verify stability
bpy.context.scene.frame_end = 250