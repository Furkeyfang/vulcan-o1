import bpy
import math
from mathutils import Vector, Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Parameters from summary
R = 5.0
strut_cross = 0.2
joint_rad = 0.15
mass_per_strut = 66.6667
total_mass = 200.0
num_struts = 3

# Vertices on sphere (pre-calculated)
v1 = Vector((5.0, 0.0, 0.0))
v2 = Vector((2.5, 4.330127, 0.0))
v3 = Vector((1.083333, 0.625, 4.330127))

# Create joint spheres at vertices
vertices = [v1, v2, v3]
joint_objects = []

for i, vert in enumerate(vertices):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=joint_rad, location=vert)
    joint = bpy.context.active_object
    joint.name = f"Joint_{i}"
    bpy.ops.rigidbody.object_add()
    joint.rigid_body.type = 'PASSIVE'
    joint.rigid_body.collision_shape = 'SPHERE'
    joint_objects.append(joint)

# Function to create strut between two points
def create_strut(end1, end2, name, mass):
    # Calculate strut properties
    direction = end2 - end1
    length = direction.length
    center = (end1 + end2) / 2
    
    # Create cube and scale to strut dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    strut = bpy.context.active_object
    strut.name = name
    
    # Scale: cross-section in X and Y, length in Z
    strut.scale = (strut_cross/2, strut_cross/2, length/2)
    
    # Rotate to align with direction vector
    # Default cube local Z is along global Z, need to rotate to direction
    up = Vector((0, 0, 1))
    rot_quat = up.rotation_difference(direction)
    strut.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    strut.rigid_body.type = 'ACTIVE'
    strut.rigid_body.mass = mass
    strut.rigid_body.collision_shape = 'BOX'
    strut.rigid_body.friction = 0.5
    strut.rigid_body.restitution = 0.1
    
    return strut

# Create three struts
strut1 = create_strut(v1, v2, "Strut_1", mass_per_strut)
strut2 = create_strut(v2, v3, "Strut_2", mass_per_strut)
strut3 = create_strut(v3, v1, "Strut_3", mass_per_strut)

# Create fixed constraints between struts and joints
def create_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    
    constraint = obj_a.rigid_body.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    # Set constraint limits to prevent any movement
    constraint.use_limit_lin_x = True
    constraint.use_limit_lin_y = True
    constraint.use_limit_lin_z = True
    constraint.limit_lin_x_lower = 0
    constraint.limit_lin_x_upper = 0
    constraint.limit_lin_y_lower = 0
    constraint.limit_lin_y_upper = 0
    constraint.limit_lin_z_lower = 0
    constraint.limit_lin_z_upper = 0
    
    constraint.use_limit_ang_x = True
    constraint.use_limit_ang_y = True
    constraint.use_limit_ang_z = True
    constraint.limit_ang_x_lower = 0
    constraint.limit_ang_x_upper = 0
    constraint.limit_ang_y_lower = 0
    constraint.limit_ang_y_upper = 0
    constraint.limit_ang_z_lower = 0
    constraint.limit_ang_z_upper = 0

# Connect struts to joints
create_fixed_constraint(strut1, joint_objects[0])  # Strut1 to Joint1 (v1)
create_fixed_constraint(strut1, joint_objects[1])  # Strut1 to Joint2 (v2)
create_fixed_constraint(strut2, joint_objects[1])  # Strut2 to Joint2 (v2)
create_fixed_constraint(strut2, joint_objects[2])  # Strut2 to Joint3 (v3)
create_fixed_constraint(strut3, joint_objects[2])  # Strut3 to Joint3 (v3)
create_fixed_constraint(strut3, joint_objects[0])  # Strut3 to Joint1 (v1)

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Set gravity
bpy.context.scene.rigidbody_world.gravity[2] = -9.8

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100

# Bake simulation (headless compatible)
bpy.ops.ptcache.free_bake_all()
bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=100)

print("Geodesic dome segment constructed with rigid joints and 200kg distributed load")
print(f"Structure has {num_struts} struts with mass {mass_per_strut} kg each")
print("Fixed constraints ensure rigid connections at all vertices")