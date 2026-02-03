import bpy
import math
from mathutils import Matrix, Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 5.0
rafter_length = 5.0
rafter_width = 0.2
rafter_depth = 0.3
tie_length = 5.0
tie_width = 0.2
tie_depth = 0.3
king_length = 2.0
king_width = 0.2
king_depth = 0.2
strut_length = 2.5
strut_width = 0.15
strut_depth = 0.15
apex_z = 4.330127
left_anchor = Vector((-2.5, 0.0, 0.0))
right_anchor = Vector((2.5, 0.0, 0.0))
tie_center = Vector((0.0, 0.0, 0.15))
king_bottom_z = 2.330127
king_center = Vector((0.0, 0.0, 3.330127))
left_rafter_mid = Vector((-1.25, 0.0, 2.1650635))
right_rafter_mid = Vector((1.25, 0.0, 2.1650635))
strut_scale_factor = 0.6828
load_mass = 180.0
wood_density = 500.0

# Helper: Create a beam with given dimensions, location, rotation
def create_beam(name, size, location, rotation_euler):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.rotation_euler = rotation_euler
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    # Calculate volume and set mass
    volume = size.x * size.y * size.z
    obj.rigid_body.mass = volume * wood_density
    return obj

# Helper: Create a fixed constraint between two objects
def create_fixed_constraint(obj1, obj2):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj1.name}_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Create Ground (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create Tie Beam
tie_size = Vector((tie_length, tie_width, tie_depth))
tie = create_beam("TieBeam", tie_size, tie_center, (0,0,0))
# Add load mass
tie.rigid_body.mass += load_mass

# Create King Post
king_size = Vector((king_width, king_depth, king_length))
king = create_beam("KingPost", king_size, king_center, (0,0,0))

# Create Left Rafter
rafter_dir_left = Vector((0,0,apex_z)) - left_anchor
rafter_len = rafter_dir_left.length
# Rotation: align X-axis (default cube length) with rafter direction
# We'll use a rotation matrix: rotate around Y axis by angle between rafter_dir and X-axis
angle_y = math.atan2(rafter_dir_left.z, rafter_dir_left.x)
rafter_size = Vector((rafter_length, rafter_width, rafter_depth))
# Location: midpoint of rafter
rafter_mid_left = (left_anchor + Vector((0,0,apex_z))) / 2
left_rafter = create_beam("LeftRafter", rafter_size, rafter_mid_left, (0, -angle_y, 0))

# Create Right Rafter
rafter_dir_right = Vector((0,0,apex_z)) - right_anchor
angle_y = math.atan2(rafter_dir_right.z, rafter_dir_right.x)
rafter_mid_right = (right_anchor + Vector((0,0,apex_z))) / 2
right_rafter = create_beam("RightRafter", rafter_size, rafter_mid_right, (0, -angle_y, 0))

# Create Left Strut
strut_dir_left = left_rafter_mid - king_center
strut_len = strut_dir_left.length
# Scale factor to fit actual length
strut_size = Vector((strut_length * strut_scale_factor, strut_width, strut_depth))
strut_mid_left = (king_center + left_rafter_mid) / 2
# Rotation: align X-axis with strut_dir_left
angle_y = math.atan2(strut_dir_left.z, strut_dir_left.x)
left_strut = create_beam("LeftStrut", strut_size, strut_mid_left, (0, -angle_y, 0))

# Create Right Strut
strut_dir_right = right_rafter_mid - king_center
strut_size = Vector((strut_length * strut_scale_factor, strut_width, strut_depth))
strut_mid_right = (king_center + right_rafter_mid) / 2
angle_y = math.atan2(strut_dir_right.z, strut_dir_right.x)
right_strut = create_beam("RightStrut", strut_size, strut_mid_right, (0, -angle_y, 0))

# Create Fixed Constraints
# 1. Rafter bases to Ground
create_fixed_constraint(left_rafter, ground)
create_fixed_constraint(right_rafter, ground)
# 2. Tie beam ends to Rafter bases (approximate: tie beam ends at anchor points)
create_fixed_constraint(tie, left_rafter)
create_fixed_constraint(tie, right_rafter)
# 3. King Post bottom to Tie beam center
create_fixed_constraint(king, tie)
# 4. King Post top to both Rafters at apex (three-way joint: two constraints)
create_fixed_constraint(king, left_rafter)
create_fixed_constraint(king, right_rafter)
# 5. Struts connections
create_fixed_constraint(left_strut, king)
create_fixed_constraint(left_strut, left_rafter)
create_fixed_constraint(right_strut, king)
create_fixed_constraint(right_strut, right_rafter)

# Set gravity to default (9.81 m/s²) for simulation
bpy.context.scene.gravity = (0, 0, -9.81)

# Optional: Set rigid body damping to reduce oscillation
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.linear_damping = 0.5
        obj.rigid_body.angular_damping = 0.5

print("King Post truss constructed with rigid bodies and fixed constraints.")