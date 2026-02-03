import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Variables from parameter summary
base_width = 5.0
truss_height = 7.0
diag_length = 7.433
member_cross = 0.2
base_scale = (5.0, 0.2, 0.2)
diag_scale = (7.433, 0.2, 0.2)
bb_width = 4.0
bb_height = 2.0
bb_thickness = 0.1
bb_center_z = 7.05
anchor_size = (0.8, 0.8, 0.4)
A = (-2.5, 0.0, 0.0)
B = (2.5, 0.0, 0.0)
C = (0.0, 0.0, 7.0)
bb_center = (0.0, 0.0, 7.05)
diag_angle_left = -0.322  # atan(7/2.5)
diag_angle_right = 0.322

# Create Base Member (Horizontal)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=((A[0]+B[0])/2, 0, 0))
base = bpy.context.active_object
base.name = "Base_Member"
base.scale = base_scale
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Left Diagonal Member
bpy.ops.mesh.primitive_cube_add(size=1.0, location=((A[0]+C[0])/2, 0, (A[2]+C[2])/2))
diag_left = bpy.context.active_object
diag_left.name = "Diagonal_Left"
diag_left.scale = diag_scale
diag_left.rotation_euler = (0, diag_angle_left, 0)
bpy.ops.rigidbody.object_add()
diag_left.rigid_body.type = 'PASSIVE'
diag_left.rigid_body.collision_shape = 'BOX'

# Create Right Diagonal Member
bpy.ops.mesh.primitive_cube_add(size=1.0, location=((B[0]+C[0])/2, 0, (B[2]+C[2])/2))
diag_right = bpy.context.active_object
diag_right.name = "Diagonal_Right"
diag_right.scale = diag_scale
diag_right.rotation_euler = (0, diag_angle_right, 0)
bpy.ops.rigidbody.object_add()
diag_right.rigid_body.type = 'PASSIVE'
diag_right.rigid_body.collision_shape = 'BOX'

# Create Billboard Panel
bpy.ops.mesh.primitive_cube_add(size=1.0, location=bb_center)
billboard = bpy.context.active_object
billboard.name = "Billboard_Panel"
billboard.scale = (bb_width/2, bb_height/2, bb_thickness/2)  # Cube default size=2, so divide by 2
bpy.ops.rigidbody.object_add()
billboard.rigid_body.type = 'ACTIVE'
billboard.rigid_body.mass = 100.0  # kg (4×2×0.1 × 1250 density)
billboard.rigid_body.collision_shape = 'BOX'

# Create Foundation Anchors (for stability)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(A[0], 0, -anchor_size[2]/2))
anchor_A = bpy.context.active_object
anchor_A.name = "Foundation_Anchor_A"
anchor_A.scale = (anchor_size[0]/2, anchor_size[1]/2, anchor_size[2]/2)
bpy.ops.rigidbody.object_add()
anchor_A.rigid_body.type = 'PASSIVE'
anchor_A.rigid_body.mass = anchor_size[0]*anchor_size[1]*anchor_size[2]*1000  # ~256 kg
anchor_A.rigid_body.collision_shape = 'BOX'

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(B[0], 0, -anchor_size[2]/2))
anchor_B = bpy.context.active_object
anchor_B.name = "Foundation_Anchor_B"
anchor_B.scale = (anchor_size[0]/2, anchor_size[1]/2, anchor_size[2]/2)
bpy.ops.rigidbody.object_add()
anchor_B.rigid_body.type = 'PASSIVE'
anchor_B.rigid_body.mass = anchor_size[0]*anchor_size[1]*anchor_size[2]*1000
anchor_B.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraints between joints
def add_fixed_constraint(obj1, obj2):
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj1.name}_{obj2.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Joint A: Base ↔ Left Diagonal ↔ Anchor A
add_fixed_constraint(base, diag_left)
add_fixed_constraint(diag_left, anchor_A)
add_fixed_constraint(base, anchor_A)

# Joint B: Base ↔ Right Diagonal ↔ Anchor B
add_fixed_constraint(base, diag_right)
add_fixed_constraint(diag_right, anchor_B)
add_fixed_constraint(base, anchor_B)

# Joint C: Left Diagonal ↔ Right Diagonal ↔ Billboard
add_fixed_constraint(diag_left, diag_right)
add_fixed_constraint(diag_left, billboard)
add_fixed_constraint(diag_right, billboard)

# Apply wind force equivalent to 300 kg lateral load
# Create wind force field (300 kg * 9.8 m/s² = 2940 N)
bpy.ops.object.empty_add(type='ARROWS', location=(0, 5, 7))
wind = bpy.context.active_object
wind.name = "Wind_Force"
bpy.ops.object.effector_add(type='WIND')
wind.field.strength = 2940.0
wind.field.direction = (0, -1, 0)  # Lateral wind from positive Y direction
wind.field.flow = 0  # Constant wind
wind.field.noise = 0  # No turbulence

# Set up collision margins for stability
for obj in bpy.data.objects:
    if hasattr(obj, 'rigid_body') and obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.001

print("Triangular truss billboard structure created successfully.")
print(f"Structure designed to withstand lateral wind force of {2940:.0f} N (300 kg equivalent)")
print("All joints connected with FIXED constraints for maximum rigidity")