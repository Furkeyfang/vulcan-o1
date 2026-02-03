import bpy
import math
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_size = (2.0, 2.0, 0.5)
apex_size = (1.0, 1.0, 0.5)
triangle_side = 3.0
base_z = 0.25
total_h = 6.0
apex_z = 5.75
v1 = mathutils.Vector((0.0, 0.0, base_z))
v2 = mathutils.Vector((triangle_side, 0.0, base_z))
v3 = mathutils.Vector((triangle_side/2, triangle_side * math.sqrt(3)/2, base_z))
apex_center = mathutils.Vector((triangle_side/2, triangle_side * math.sqrt(3)/6, apex_z))
member_section = 0.3
load_mass = 100.0
load_rad = 0.25
load_pos = apex_center + mathutils.Vector((0, 0, 0.5))

# Function to create cube with physics
def create_cube(name, size, location, scale_factors=(1,1,1)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    cube = bpy.context.active_object
    cube.name = name
    cube.scale = (size[0]/2 * scale_factors[0], 
                  size[1]/2 * scale_factors[1], 
                  size[2]/2 * scale_factors[2])
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.type = 'PASSIVE'
    return cube

# Function to create inclined member between two points
def create_member(name, start, end, section):
    # Calculate midpoint and orientation
    midpoint = (start + end) / 2
    direction = end - start
    length = direction.length
    
    # Create cube at origin then transform
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
    member = bpy.context.active_object
    member.name = name
    
    # Scale: section width/depth, length in Z
    member.scale = (section/2, section/2, length/2)
    
    # Rotate to align with direction vector
    up = mathutils.Vector((0, 0, 1))
    rot_quat = up.rotation_difference(direction)
    member.rotation_mode = 'QUATERNION'
    member.rotation_quaternion = rot_quat
    
    # Move to midpoint
    member.location = midpoint
    
    # Add physics
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'PASSIVE'
    return member

# Create base triangle cubes
base1 = create_cube("Base_Cube_1", base_size, v1)
base2 = create_cube("Base_Cube_2", base_size, v2)
base3 = create_cube("Base_Cube_3", base_size, v3)

# Create apex cube
apex = create_cube("Apex_Cube", apex_size, apex_center)

# Create inclined members
member1 = create_member("Member_1", v1, apex_center, member_section)
member2 = create_member("Member_2", v2, apex_center, member_section)
member3 = create_member("Member_3", v3, apex_center, member_section)

# Function to add fixed constraint between two objects
def add_fixed_constraint(name, obj1, obj2):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    # Move constraint to midpoint
    empty.location = (obj1.location + obj2.location) / 2

# Add constraints between base cubes and members
add_fixed_constraint("Constraint_B1_M1", base1, member1)
add_fixed_constraint("Constraint_B2_M2", base2, member2)
add_fixed_constraint("Constraint_B3_M3", base3, member3)

# Add constraints between members and apex
add_fixed_constraint("Constraint_M1_A", member1, apex)
add_fixed_constraint("Constraint_M2_A", member2, apex)
add_fixed_constraint("Constraint_M3_A", member3, apex)

# Create load sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=load_rad, location=load_pos)
load_sphere = bpy.context.active_object
load_sphere.name = "Load_Sphere"
bpy.ops.rigidbody.object_add()
load_sphere.rigid_body.type = 'ACTIVE'
load_sphere.rigid_body.mass = load_mass

# Set up simulation parameters
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Tetrahedral tower construction complete. Simulation ready for 100 frames.")