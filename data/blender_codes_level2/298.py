import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
num_cubes = 10
base_width = 4.0
top_width = 1.5
cube_height = 3.0
total_height = 30.0
load_size = 1.0
load_mass = 2500.0
base_cube_center_z = 1.5
load_cube_center_z = 30.5

# Width decrement per cube
width_step = (base_width - top_width) / (num_cubes - 1)

# List to store cube objects for constraints
cube_objects = []

# Create tapered tower cubes
for i in range(num_cubes):
    # Calculate current width/depth (linearly decreasing)
    current_width = base_width - width_step * i
    current_depth = current_width  # Equal to width as per task
    
    # Calculate Z position (stacked vertically)
    cube_z = base_cube_center_z + i * cube_height
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, cube_z))
    cube = bpy.context.active_object
    cube.scale = (current_width, current_depth, cube_height)
    cube.name = f"TowerCube_{i}"
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    
    # First cube (base) is passive, others active
    if i == 0:
        cube.rigid_body.type = 'PASSIVE'
    else:
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = cube.scale.x * cube.scale.y * cube.scale.z * 2400  # Concrete density ~2400 kg/m³
    
    cube_objects.append(cube)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, load_cube_center_z))
load_cube = bpy.context.active_object
load_cube.scale = (load_size, load_size, load_size)
load_cube.name = "LoadCube"

# Add rigid body to load with specified mass
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_mass

# Create fixed constraints between cubes
for i in range(1, num_cubes):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"FixedConstraint_{i-1}_to_{i}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link constraint to the two cubes
    constraint.object1 = cube_objects[i-1]
    constraint.object2 = cube_objects[i]

# Create fixed constraint between top cube and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
top_constraint = bpy.context.active_object
top_constraint.name = "TopToLoad_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = top_constraint.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = cube_objects[-1]  # Top cube
constraint.object2 = load_cube

# Set world physics for simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 250  # Sufficient frames for stabilization

print(f"Tower constructed with {num_cubes} cubes, total height: {total_height}m")
print(f"Load cube mass: {load_mass}kg at Z={load_cube_center_z}m")