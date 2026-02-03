import bpy
import math

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Define parameters from summary
span = 6.0
w = 0.2  # member cross-section width (Y)
d = 0.2  # member cross-section depth (Z)
bot_z = 0.5
v_height = 1.5
top_z = 2.0
diag_len = 3.35410196625
load_mass = 300.0
load_force = 2943.0
mem_mass = 10.0
g = -9.81
frames = 100

# Joint coordinates
left_end = (-span/2, 0, bot_z)
right_end = (span/2, 0, bot_z)
mid_bottom = (0, 0, bot_z)
top_point = (0, 0, top_z)

# 3. Create bottom chord (passive, fixed base)
bpy.ops.mesh.primitive_cube_add(size=1, location=mid_bottom)
bottom = bpy.context.active_object
bottom.name = "BottomChord"
bottom.scale = (span, w, d)  # X=length, Y=width, Z=depth
bpy.ops.rigidbody.object_add()
bottom.rigid_body.type = 'PASSIVE'
bottom.rigid_body.collision_shape = 'BOX'

# 4. Create vertical post (active)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, bot_z + v_height/2))
vert = bpy.context.active_object
vert.name = "VerticalPost"
vert.scale = (w, w, v_height)  # X=width, Y=width, Z=height
bpy.ops.rigidbody.object_add()
vert.rigid_body.type = 'ACTIVE'
vert.rigid_body.mass = mem_mass
vert.rigid_body.collision_shape = 'BOX'

# 5. Create left diagonal (active)
# Calculate midpoint and rotation for left diagonal
left_mid = ((left_end[0] + top_point[0])/2, 0, (left_end[2] + top_point[2])/2)
dx = top_point[0] - left_end[0]
dz = top_point[2] - left_end[2]
angle_z = math.atan2(dz, dx)  # rotation around Y axis (Blender uses Z-up, so Y rotation)

bpy.ops.mesh.primitive_cube_add(size=1, location=left_mid)
left_diag = bpy.context.active_object
left_diag.name = "LeftDiagonal"
left_diag.scale = (diag_len, w, d)  # length along local X
left_diag.rotation_euler = (0, angle_z, 0)  # rotate around Y axis
bpy.ops.rigidbody.object_add()
left_diag.rigid_body.type = 'ACTIVE'
left_diag.rigid_body.mass = mem_mass
left_diag.rigid_body.collision_shape = 'BOX'

# 6. Create right diagonal (active)
right_mid = ((right_end[0] + top_point[0])/2, 0, (right_end[2] + top_point[2])/2)
dx = top_point[0] - right_end[0]  # negative 3
angle_z = math.atan2(dz, dx)  # different angle due to negative dx

bpy.ops.mesh.primitive_cube_add(size=1, location=right_mid)
right_diag = bpy.context.active_object
right_diag.name = "RightDiagonal"
right_diag.scale = (diag_len, w, d)
right_diag.rotation_euler = (0, angle_z, 0)
bpy.ops.rigidbody.object_add()
right_diag.rigid_body.type = 'ACTIVE'
right_diag.rigid_body.mass = mem_mass
right_diag.rigid_body.collision_shape = 'BOX'

# 7. Create load point (small cube with 300kg mass)
bpy.ops.mesh.primitive_cube_add(size=0.1, location=top_point)
load = bpy.context.active_object
load.name = "LoadPoint"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# 8. Create FIXED constraints at all joints
def add_fixed_constraint(name, location, obj1, obj2):
    """Create a FIXED constraint between two objects at specified location"""
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{name}"
    empty.empty_display_size = 0.2
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Joint 1: Bottom-LeftDiagonal
add_fixed_constraint("J1", left_end, bottom, left_diag)
# Joint 2: Bottom-RightDiagonal  
add_fixed_constraint("J2", right_end, bottom, right_diag)
# Joint 3: Bottom-Vertical
add_fixed_constraint("J3", mid_bottom, bottom, vert)
# Joint 4: Vertical-LeftDiagonal
add_fixed_constraint("J4", top_point, vert, left_diag)
# Joint 5: Vertical-RightDiagonal
add_fixed_constraint("J5", top_point, vert, right_diag)
# Joint 6: Load-Vertical
add_fixed_constraint("J6", top_point, load, vert)
# Joint 7: Load-LeftDiagonal
add_fixed_constraint("J7", top_point, load, left_diag)
# Joint 8: Load-RightDiagonal
add_fixed_constraint("J8", top_point, load, right_diag)

# 9. Set physics world parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = frames

# 10. Ensure bottom chord is immovable (passive rigid body with no constraints to move it)
# This simulates fixed supports at both ends

print(f"King Post truss created with {frames} frame simulation")
print(f"Load: {load_mass}kg ({load_force}N) at top joint")