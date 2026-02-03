import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
foundation_size = (2.0, 2.0, 1.0)
foundation_location = (0.0, 0.0, 0.5)
cube_size = (0.5, 0.5, 1.0)
cube_count = 14
base_offset_x = 0.4
bottom_cube_location = (base_offset_x, 0.0, 1.5)
load_mass_kg = 1200.0
cube_density_kgm3 = 2400.0

# Calculate cube mass from density and volume
cube_volume = cube_size[0] * cube_size[1] * cube_size[2]
cube_mass_kg = cube_volume * cube_density_kgm3

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Create foundation block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=foundation_location)
foundation = bpy.context.active_object
foundation.name = "Foundation"
foundation.scale = foundation_size
bpy.ops.rigidbody.object_add()
foundation.rigid_body.type = 'PASSIVE'
foundation.rigid_body.collision_shape = 'BOX'
foundation.rigid_body.mass = foundation_size[0] * foundation_size[1] * foundation_size[2] * cube_density_kgm3

# Create and store cube objects
cubes = []
for i in range(cube_count):
    # Calculate position for this cube
    z_pos = bottom_cube_location[2] + i * cube_size[2]  # Stack vertically
    cube_location = (bottom_cube_location[0], bottom_cube_location[1], z_pos)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=cube_location)
    cube = bpy.context.active_object
    cube.name = f"FrameCube_{i+1:02d}"
    cube.scale = cube_size
    
    # Add rigid body properties
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.type = 'ACTIVE'
    cube.rigid_body.collision_shape = 'BOX'
    cube.rigid_body.mass = cube_mass_kg
    
    cubes.append(cube)

# Apply additional mass to top cube to represent 1200kg load
top_cube = cubes[-1]
top_cube.rigid_body.mass = cube_mass_kg + load_mass_kg

# Create FIXED constraints between elements
def create_fixed_constraint(obj_a, obj_b, constraint_name):
    """Create a FIXED constraint between two objects"""
    # Create empty object for constraint
    bpy.ops.object.add(type='EMPTY', location=obj_a.location)
    constraint_obj = bpy.context.active_object
    constraint_obj.name = constraint_name
    constraint_obj.empty_display_size = 0.2
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint_obj.rigid_body_constraint.type = 'FIXED'
    constraint_obj.rigid_body_constraint.object1 = obj_a
    constraint_obj.rigid_body_constraint.object2 = obj_b
    
    # Set constraint limits (all locked for FIXED)
    constraint_obj.rigid_body_constraint.use_limit_lin_x = True
    constraint_obj.rigid_body_constraint.use_limit_lin_y = True
    constraint_obj.rigid_body_constraint.use_limit_lin_z = True
    constraint_obj.rigid_body_constraint.use_limit_ang_x = True
    constraint_obj.rigid_body_constraint.use_limit_ang_y = True
    constraint_obj.rigid_body_constraint.use_limit_ang_z = True
    
    # Set linear limits to zero (no movement)
    constraint_obj.rigid_body_constraint.limit_lin_x_lower = 0.0
    constraint_obj.rigid_body_constraint.limit_lin_x_upper = 0.0
    constraint_obj.rigid_body_constraint.limit_lin_y_lower = 0.0
    constraint_obj.rigid_body_constraint.limit_lin_y_upper = 0.0
    constraint_obj.rigid_body_constraint.limit_lin_z_lower = 0.0
    constraint_obj.rigid_body_constraint.limit_lin_z_upper = 0.0
    
    # Set angular limits to zero (no rotation)
    constraint_obj.rigid_body_constraint.limit_ang_x_lower = 0.0
    constraint_obj.rigid_body_constraint.limit_ang_x_upper = 0.0
    constraint_obj.rigid_body_constraint.limit_ang_y_lower = 0.0
    constraint_obj.rigid_body_constraint.limit_ang_y_upper = 0.0
    constraint_obj.rigid_body_constraint.limit_ang_z_lower = 0.0
    constraint_obj.rigid_body_constraint.limit_ang_z_upper = 0.0

# Constrain foundation to bottom cube
create_fixed_constraint(foundation, cubes[0], "Foundation_BaseConstraint")

# Constrain adjacent cubes in the stack
for i in range(cube_count - 1):
    create_fixed_constraint(cubes[i], cubes[i+1], f"Constraint_Cube{i+1:02d}_to_Cube{i+2:02d}")

# Set simulation parameters for stability
bpy.context.scene.rigidbody_world.steps_per_second = 200
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Position camera for better view
bpy.ops.object.camera_add(location=(10.0, -10.0, 10.0))
camera = bpy.context.active_object
camera.rotation_euler = (0.7854, 0.0, 0.5236)  # 45° pitch, 30° yaw
bpy.context.scene.camera = camera

print(f"Structure created with {cube_count} stacked cubes")
print(f"Base offset: {base_offset_x}m in X-direction")
print(f"Total height: {bottom_cube_location[2] + (cube_count-1)*cube_size[2] + cube_size[2]/2}m")
print(f"Load mass applied to top cube: {load_mass_kg}kg")