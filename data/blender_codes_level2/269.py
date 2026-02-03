import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
H = 10.0
P = 2.0
R = 1.0
cw = 0.2
cd = 0.2
ch = 0.5
cubes_per_rev = 12
total_rev = 5
total_cubes = 60
angular_step = 2 * math.pi / cubes_per_rev
load_mass = 200.0
plate_thick = 0.1
plate_rad = 1.2

# Collection for organization
bpy.ops.object.collection_add()
main_collection = bpy.context.collection

# Create base cube (passive anchor)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -ch/2))
base = bpy.context.active_object
base.scale = (cw, cd, ch)
base.name = "Base_Anchor"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create helical cubes
cubes = []
for i in range(total_cubes):
    theta = i * angular_step
    z = (P / (2 * math.pi)) * theta
    
    # Helical coordinates
    x = R * math.cos(theta)
    y = R * math.sin(theta)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    cube = bpy.context.active_object
    cube.scale = (cw, cd, ch)
    cube.name = f"Helix_Cube_{i:03d}"
    
    # Orient cube along helix tangent
    tangent = Vector([-R * math.sin(theta), R * math.cos(theta), P/(2*math.pi)])
    tangent.normalize()
    
    # Align local Z axis to tangent
    up = Vector((0, 0, 1))
    rot_quat = up.rotation_difference(tangent)
    cube.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.mass = load_mass / cubes_per_rev
    cube.rigid_body.collision_shape = 'BOX'
    
    cubes.append(cube)

# Create fixed constraints between cubes
for i in range(1, total_cubes):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=cubes[i].location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Fixed_Constraint_{i-1:03d}"
    
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link constraint to adjacent cubes
    constraint.object1 = cubes[i-1]
    constraint.object2 = cubes[i]

# Connect first cube to base
bpy.ops.object.empty_add(type='PLAIN_AXES', location=cubes[0].location)
base_constraint = bpy.context.active_object
base_constraint.name = "Base_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = base_constraint.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = base
constraint.object2 = cubes[0]

# Create load plates at each revolution
for n in range(1, total_rev + 1):
    theta_plate = 2 * math.pi * n
    z_plate = P * n
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_plate))
    plate = bpy.context.active_object
    plate.scale = (plate_rad, plate_rad, plate_thick)
    plate.name = f"Load_Plate_{n}"
    
    # Add rigid body with distributed mass
    bpy.ops.rigidbody.object_add()
    plate.rigid_body.mass = load_mass
    plate.rigid_body.collision_shape = 'BOX'
    
    # Find nearest cubes for connection (within same revolution)
    cube_indices = [(n-1)*cubes_per_rev + i for i in range(cubes_per_rev)]
    nearest_cubes = [cubes[idx % total_cubes] for idx in cube_indices]
    
    # Connect plate to multiple cubes for load distribution
    for j, cube in enumerate(nearest_cubes[:4]):  # Connect to 4 cubes for stability
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=((cube.location + plate.location)/2))
        plate_constraint = bpy.context.active_object
        plate_constraint.name = f"Plate_Constraint_{n}_{j}"
        
        bpy.ops.rigidbody.constraint_add()
        constraint = plate_constraint.rigid_body_constraint
        constraint.type = 'FIXED'
        constraint.object1 = plate
        constraint.object2 = cube

# Set world physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.use_split_impulse = True

print(f"Helical tower constructed with {total_cubes} cubes and {total_rev} load plates")